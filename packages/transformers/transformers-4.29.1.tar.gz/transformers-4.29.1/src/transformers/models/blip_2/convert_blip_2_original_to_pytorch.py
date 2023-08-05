# coding=utf-8
# Copyright 2023 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Convert BLIP-2 checkpoints from the original repository.

URL: https://github.com/salesforce/LAVIS/tree/main/projects/blip2
"""

import argparse

import requests
import torch

# pip3 install salesforce-lavis
# I'm actually installing a slightly modified version: pip3 install git+https://github.com/nielsrogge/LAVIS.git@fix_lavis
from lavis.models import load_model_and_preprocess
from PIL import Image

from transformers import (
    AutoTokenizer,
    Blip2Config,
    Blip2ForConditionalGeneration,
    Blip2Processor,
    Blip2VisionConfig,
    BlipImageProcessor,
    OPTConfig,
    T5Config,
)
from transformers.utils.constants import OPENAI_CLIP_MEAN, OPENAI_CLIP_STD


def load_demo_image():
    url = "https://storage.googleapis.com/sfr-vision-language-research/LAVIS/assets/merlion.png"
    image = Image.open(requests.get(url, stream=True).raw).convert("RGB")

    return image


# here we list all keys to be renamed (original name on the left, our name on the right)
def create_rename_keys(config):
    rename_keys = []
    # fmt: off

    # vision encoder
    rename_keys.append(("visual_encoder.cls_token", "vision_model.embeddings.class_embedding"))
    rename_keys.append(("visual_encoder.pos_embed", "vision_model.embeddings.position_embedding"))
    rename_keys.append(("visual_encoder.patch_embed.proj.weight", "vision_model.embeddings.patch_embedding.weight"))
    rename_keys.append(("visual_encoder.patch_embed.proj.bias", "vision_model.embeddings.patch_embedding.bias"))
    rename_keys.append(("ln_vision.weight", "vision_model.post_layernorm.weight"))
    rename_keys.append(("ln_vision.bias", "vision_model.post_layernorm.bias"))

    for i in range(config.vision_config.num_hidden_layers):
        rename_keys.append((f"visual_encoder.blocks.{i}.norm1.weight", f"vision_model.encoder.layers.{i}.layer_norm1.weight"))
        rename_keys.append((f"visual_encoder.blocks.{i}.norm1.bias", f"vision_model.encoder.layers.{i}.layer_norm1.bias"))
        rename_keys.append((f"visual_encoder.blocks.{i}.norm2.weight", f"vision_model.encoder.layers.{i}.layer_norm2.weight"))
        rename_keys.append((f"visual_encoder.blocks.{i}.norm2.bias", f"vision_model.encoder.layers.{i}.layer_norm2.bias"))
        rename_keys.append((f"visual_encoder.blocks.{i}.attn.qkv.weight", f"vision_model.encoder.layers.{i}.self_attn.qkv.weight"))
        rename_keys.append((f"visual_encoder.blocks.{i}.attn.proj.weight", f"vision_model.encoder.layers.{i}.self_attn.projection.weight",))
        rename_keys.append((f"visual_encoder.blocks.{i}.attn.proj.bias", f"vision_model.encoder.layers.{i}.self_attn.projection.bias"))
        rename_keys.append((f"visual_encoder.blocks.{i}.mlp.fc1.weight", f"vision_model.encoder.layers.{i}.mlp.fc1.weight"))
        rename_keys.append((f"visual_encoder.blocks.{i}.mlp.fc1.bias", f"vision_model.encoder.layers.{i}.mlp.fc1.bias"))
        rename_keys.append((f"visual_encoder.blocks.{i}.mlp.fc2.weight", f"vision_model.encoder.layers.{i}.mlp.fc2.weight"))
        rename_keys.append((f"visual_encoder.blocks.{i}.mlp.fc2.bias", f"vision_model.encoder.layers.{i}.mlp.fc2.bias"))

    # QFormer
    rename_keys.append(("Qformer.bert.embeddings.LayerNorm.weight", "qformer.layernorm.weight"))
    rename_keys.append(("Qformer.bert.embeddings.LayerNorm.bias", "qformer.layernorm.bias"))

    # fmt: on
    return rename_keys


def rename_key(dct, old, new):
    val = dct.pop(old)
    dct[new] = val


def read_in_q_v_bias(state_dict, config):
    for i in range(config.vision_config.num_hidden_layers):
        # read in original q and v biases
        q_bias = state_dict.pop(f"visual_encoder.blocks.{i}.attn.q_bias")
        v_bias = state_dict.pop(f"visual_encoder.blocks.{i}.attn.v_bias")

        # next, set bias in the state dict
        qkv_bias = torch.cat((q_bias, torch.zeros_like(v_bias, requires_grad=False), v_bias))
        state_dict[f"vision_model.encoder.layers.{i}.self_attn.qkv.bias"] = qkv_bias


def get_blip2_config(model_name, eos_token_id):
    image_size = 364 if "coco" in model_name else 224
    vision_config = Blip2VisionConfig(image_size=image_size).to_dict()

    # make sure the models have proper bos_token_id and eos_token_id set (important for generation)
    # seems like flan-T5 models don't have bos_token_id properly set?
    if "opt-2.7b" in model_name:
        text_config = OPTConfig.from_pretrained("facebook/opt-2.7b", eos_token_id=eos_token_id).to_dict()
    elif "opt-6.7b" in model_name:
        text_config = OPTConfig.from_pretrained("facebook/opt-6.7b", eos_token_id=eos_token_id).to_dict()
    elif "t5-xl" in model_name:
        text_config = T5Config.from_pretrained("google/flan-t5-xl", dense_act_fn="gelu", bos_token_id=1).to_dict()
    elif "t5-xxl" in model_name:
        text_config = T5Config.from_pretrained("google/flan-t5-xxl", dense_act_fn="gelu", bos_token_id=1).to_dict()

    config = Blip2Config(vision_config=vision_config, text_config=text_config)

    return config, image_size


@torch.no_grad()
def convert_blip2_checkpoint(model_name, pytorch_dump_folder_path=None, push_to_hub=False):
    """
    Copy/paste/tweak model's weights to Transformers design.
    """
    tokenizer = (
        AutoTokenizer.from_pretrained("facebook/opt-2.7b")
        if "opt" in model_name
        else AutoTokenizer.from_pretrained("google/flan-t5-xl")
    )
    eos_token_id = tokenizer("\n", add_special_tokens=False).input_ids[0]
    config, image_size = get_blip2_config(model_name, eos_token_id=eos_token_id)

    hf_model = Blip2ForConditionalGeneration(config).eval()

    model_name_to_original = {
        "blip2-opt-2.7b": ("blip2_opt", "pretrain_opt2.7b"),
        "blip2-opt-6.7b": ("blip2_opt", "pretrain_opt6.7b"),
        "blip2-opt-2.7b-coco": ("blip2_opt", "caption_coco_opt2.7b"),
        "blip2-opt-6.7b-coco": ("blip2_opt", "caption_coco_opt6.7b"),
        "blip2-flan-t5-xl": ("blip2_t5", "pretrain_flant5xl"),
        "blip2-flan-t5-xl-coco": ("blip2_t5", "caption_coco_flant5xl"),
        "blip2-flan-t5-xxl": ("blip2_t5", "pretrain_flant5xxl"),
    }

    name, type = model_name_to_original[model_name]

    # load original model
    print("Loading original model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    original_model, vis_processors, _ = load_model_and_preprocess(
        name=name, model_type=type, is_eval=True, device=device
    )
    original_model.eval()
    print("Done!")

    # update state dict keys
    state_dict = original_model.state_dict()
    rename_keys = create_rename_keys(config)
    for src, dest in rename_keys:
        rename_key(state_dict, src, dest)

    # some keys can be renamed efficiently
    for key, val in state_dict.copy().items():
        val = state_dict.pop(key)
        if key.startswith("Qformer.bert"):
            key = key.replace("Qformer.bert", "qformer")
        if "attention.self" in key:
            key = key.replace("self", "attention")
        if "opt_proj" in key:
            key = key.replace("opt_proj", "language_projection")
        if "t5_proj" in key:
            key = key.replace("t5_proj", "language_projection")
        if key.startswith("opt"):
            key = key.replace("opt", "language")
        if key.startswith("t5"):
            key = key.replace("t5", "language")
        state_dict[key] = val

    # read in qv biases
    read_in_q_v_bias(state_dict, config)

    missing_keys, unexpected_keys = hf_model.load_state_dict(state_dict, strict=False)
    assert len(missing_keys) == 0
    assert unexpected_keys == ["qformer.embeddings.position_ids"]

    image = load_demo_image()
    original_pixel_values = vis_processors["eval"](image).unsqueeze(0).to(device)
    input_ids = tokenizer(["\n"], return_tensors="pt").input_ids.to(device)

    # create processor
    image_processor = BlipImageProcessor(
        size={"height": image_size, "width": image_size}, image_mean=OPENAI_CLIP_MEAN, image_std=OPENAI_CLIP_STD
    )
    processor = Blip2Processor(image_processor=image_processor, tokenizer=tokenizer)
    pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)

    # make sure processor creates exact same pixel values
    assert torch.allclose(pixel_values, original_pixel_values)

    original_model.to(device)
    hf_model.to(device)
    with torch.no_grad():
        if "opt" in model_name:
            original_logits = original_model({"image": original_pixel_values, "text_input": [""]}).logits
            logits = hf_model(original_pixel_values, input_ids).logits
        else:
            original_logits = original_model(
                {"image": original_pixel_values, "text_input": ["\n"], "text_output": ["\n"]}
            ).logits
            labels = input_ids.masked_fill(input_ids == tokenizer.pad_token_id, -100)
            logits = hf_model(original_pixel_values, input_ids, labels=labels).logits

    assert original_logits.shape == logits.shape
    print("First values of original logits:", original_logits[0, :3, :3])
    print("First values of HF logits:", logits[0, :3, :3])

    # assert values
    if model_name == "blip2-flan-t5-xl":
        expected_slice_logits = torch.tensor(
            [[-41.5850, -4.4440, -8.9922], [-47.4322, -5.9143, -1.7340]], device=device
        )
        assert torch.allclose(logits[0, :3, :3], expected_slice_logits, atol=1e-4)
    elif model_name == "blip2-flan-t5-xl-coco":
        expected_slice_logits = torch.tensor(
            [[-57.0109, -9.8967, -12.6280], [-68.6578, -12.7191, -10.5065]], device=device
        )
    else:
        # cast to same type
        target_dtype = logits.dtype
        assert torch.allclose(original_logits.to(target_dtype), logits, atol=1e-2)
    print("Looks ok!")

    print("Generating a caption...")
    prompt = ""
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)

    original_outputs = original_model.generate({"image": original_pixel_values})
    outputs = hf_model.generate(
        original_pixel_values,
        input_ids,
        do_sample=False,
        num_beams=5,
        max_length=30,
        min_length=1,
        top_p=0.9,
        repetition_penalty=1.0,
        length_penalty=1.0,
        temperature=1,
    )
    print("Original generation:", original_outputs)
    prompt_length = input_ids.shape[1]
    output_text = processor.batch_decode(outputs[:, prompt_length:], skip_special_tokens=True)
    output_text = [text.strip() for text in output_text]
    print("HF generation:", output_text)

    if pytorch_dump_folder_path is not None:
        processor.save_pretrained(pytorch_dump_folder_path)
        hf_model.save_pretrained(pytorch_dump_folder_path)

    if push_to_hub:
        processor.push_to_hub(f"nielsr/{model_name}")
        hf_model.push_to_hub(f"nielsr/{model_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    choices = [
        "blip2-opt-2.7b",
        "blip2-opt-6.7b",
        "blip2-opt-2.7b-coco",
        "blip2-opt-6.7b-coco",
        "blip2-flan-t5-xl",
        "blip2-flan-t5-xl-coco",
        "blip2-flan-t5-xxl",
    ]
    parser.add_argument(
        "--model_name",
        default="blip2-opt-2.7b",
        choices=choices,
        type=str,
        help="Path to hf config.json of model to convert",
    )
    parser.add_argument("--pytorch_dump_folder_path", default=None, type=str, help="Path to the output PyTorch model.")
    parser.add_argument(
        "--push_to_hub",
        action="store_true",
        help="Whether to push the model and processor to the hub after converting",
    )

    args = parser.parse_args()

    convert_blip2_checkpoint(args.model_name, args.pytorch_dump_folder_path, args.push_to_hub)

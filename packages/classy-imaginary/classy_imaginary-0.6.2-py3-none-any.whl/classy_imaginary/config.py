from dataclasses import dataclass
from typing import Optional

DEFAULT_MODEL = "SD-1.5"
DEFAULT_SAMPLER = "k_dpmpp_2m"

DEFAULT_NEGATIVE_PROMPT = (
    "weird eyes, smudged face, blurred face, poorly drawn face, mutation, mutilation, cloned face, strange mouth, duplicated face, "
    "Ugly, duplication, duplicates, mutilation, deformed, mutilated, mutation, twisted body, disfigured, bad anatomy, "
    "poorly drawn hands, extra limbs, malformed limbs, missing arms, extra arms, missing legs, extra legs, mutated hands, "
    "extra hands, fused fingers, missing fingers, extra fingers, long neck, small head, closed eyes, rolling eyes, "
    "grainy, blurred, blurry, writing, calligraphy, text, watermark, bad art, missing fingers, missing limbs, "
    "out of frame, extra fingers, mutated hands, porn, child abuse, horrific images, dead bodies, "
    "watermark, child, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, "
    "worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad feet, bad lighting, "
    "bad coloring, bad perspective, bad focus, bad design, bad eyes, bad hair, bad nose, bad mouth, bad ears, bad teeth, bad tongue, bad lips, "
    "nude, naked, paedophile, pedo, floating limbs, bad art, low detail, plain background, grainy, low "
    "quality, mutated hands and fingers, watermark, thin lines, deformed, signature, blurry, ugly, bad anatomy, extra"
    "limbs, undersaturated, low resolution, disfigured, deformations, out of frame, amputee, bad proportions, extra limb, missing"
    "limbs, distortion, out of frame, poorly drawn face, poorly drawn hands, text, malformed, cropped, "
    "clashing colors, pixelated, overexposed, underexposed, unbalanced composition, excessive noise, red-eye, "
    "distracting background, poor framing, tilted horizon, lack of contrast, over-saturated, lens flare, "
    "awkward pose, unflattering angle, harsh shadows, flat lighting, lack of focus, over-processed, "
    "visible artifacts, chromatic aberration, ghosting, moire patterns, banding, halo effect"
)

SPLITMEM_ENABLED = False


@dataclass
class ModelConfig:
    description: str
    short_name: str
    config_path: str
    weights_url: str
    default_image_size: int
    weights_url_full: str = None
    forced_attn_precision: str = "default"
    default_negative_prompt: str = DEFAULT_NEGATIVE_PROMPT
    alias: str = None


midas_url = "https://github.com/intel-isl/DPT/releases/download/1_0/dpt_hybrid-midas-501f0c75.pt"

MODEL_CONFIGS = [
    ModelConfig(
        description="Stable Diffusion 1.4",
        short_name="SD-1.4",
        config_path="configs/stable-diffusion-v1.yaml",
        weights_url="https://huggingface.co/bstddev/sd-v1-4/resolve/77221977fa8de8ab8f36fac0374c120bd5b53287/sd-v1-4.ckpt",
        default_image_size=512,
        alias="sd14",
    ),
    ModelConfig(
        description="Stable Diffusion 1.5",
        short_name="SD-1.5",
        config_path="configs/stable-diffusion-v1.yaml",
        weights_url="https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/889b629140e71758e1e0006e355c331a5744b4bf/v1-5-pruned-emaonly.ckpt",
        weights_url_full="https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/889b629140e71758e1e0006e355c331a5744b4bf/v1-5-pruned.ckpt",
        default_image_size=512,
        alias="sd15",
    ),
    ModelConfig(
        description="Stable Diffusion 1.5 - Inpainting",
        short_name="SD-1.5-inpaint",
        config_path="configs/stable-diffusion-v1-inpaint.yaml",
        weights_url="https://huggingface.co/julienacquaviva/inpainting/resolve/2155ff7fe38b55f4c0d99c2f1ab9b561f8311ca7/sd-v1-5-inpainting.ckpt",
        default_image_size=512,
        alias="sd15in",
    ),
    ModelConfig(
        description="Stable Diffusion 2.0 - bad at making people",
        short_name="SD-2.0",
        config_path="configs/stable-diffusion-v2-inference.yaml",
        weights_url="https://huggingface.co/stabilityai/stable-diffusion-2-base/resolve/main/512-base-ema.ckpt",
        default_image_size=512,
        alias="sd20",
    ),
    ModelConfig(
        description="Stable Diffusion 2.0 - Inpainting",
        short_name="SD-2.0-inpaint",
        config_path="configs/stable-diffusion-v2-inpainting-inference.yaml",
        weights_url="https://huggingface.co/stabilityai/stable-diffusion-2-inpainting/resolve/main/512-inpainting-ema.ckpt",
        default_image_size=512,
        alias="sd20in",
    ),
    ModelConfig(
        description="Stable Diffusion 2.1",
        short_name="SD-2.1",
        config_path="configs/stable-diffusion-v2-inference.yaml",
        weights_url="https://huggingface.co/stabilityai/stable-diffusion-2-1-base/resolve/main/v2-1_512-ema-pruned.ckpt",
        default_image_size=512,
        alias="sd21",
    ),
    ModelConfig(
        description="Stable Diffusion 2.1 - Inpainting",
        short_name="SD-2.1-inpaint",
        config_path="configs/stable-diffusion-v2-inpainting-inference.yaml",
        weights_url="https://huggingface.co/stabilityai/stable-diffusion-2-inpainting/resolve/main/512-inpainting-ema.ckpt",
        default_image_size=512,
        alias="sd21in",
    ),
    ModelConfig(
        description="Stable Diffusion 2.1 v - 768x768",
        short_name="SD-2.1-v",
        config_path="configs/stable-diffusion-v2-inference-v.yaml",
        weights_url="https://huggingface.co/stabilityai/stable-diffusion-2-1/resolve/main/v2-1_768-ema-pruned.ckpt",
        default_image_size=768,
        forced_attn_precision="fp32",
    ),
    ModelConfig(
        description="Stable Diffusion 2.0 v - 768x768",
        short_name="SD-2.0-v",
        config_path="configs/stable-diffusion-v2-inference-v.yaml",
        weights_url="https://huggingface.co/stabilityai/stable-diffusion-2/resolve/main/768-v-ema.ckpt",
        default_image_size=768,
        alias="sd20v",
    ),
    ModelConfig(
        description="Stable Diffusion 2.0 - Depth",
        short_name="SD-2.0-depth",
        config_path="configs/stable-diffusion-v2-midas-inference.yaml",
        weights_url="https://huggingface.co/stabilityai/stable-diffusion-2-depth/resolve/main/512-depth-ema.ckpt",
        default_image_size=512,
        alias="sd20dep",
    ),
    ModelConfig(
        description="Instruct Pix2Pix - Photo Editing",
        short_name="instruct-pix2pix",
        config_path="configs/instruct-pix2pix.yaml",
        weights_url="https://huggingface.co/imaginairy/instruct-pix2pix/resolve/ea0009b3d0d4888f410a40bd06d69516d0b5a577/instruct-pix2pix-00-22000-pruned.ckpt",
        default_image_size=512,
        default_negative_prompt="",
        alias="edit",
    ),
    # --- Custom models --#
    ModelConfig(
        description="OpenJourney V2",
        short_name="openjourney-v2",
        config_path="configs/stable-diffusion-v1.yaml",
        weights_url="https://huggingface.co/prompthero/openjourney-v2/resolve/47257274a40e93dab7fbc0cd2cfd5f5704cfeb60/openjourney-v2.ckpt",
        default_image_size=512,
        default_negative_prompt="",
        alias="oj2",
    ),
    ModelConfig(
        description="MidJourney PaperCut",
        short_name="MidJourney-PaperCut",
        config_path="configs/stable-diffusion-v1.yaml",
        weights_url="https://huggingface.co/ShadoWxShinigamI/MidJourney-PaperCut/resolve/main/Mdjrny-pprct_step_7000.ckpt",
        default_image_size=512,
        alias="mjpc"
    ),
    ModelConfig(
        description="Synthwave Punk",
        short_name="SynthwavePunk",
        config_path="configs/stable-diffusion-v1.yaml",
        weights_url="https://huggingface.co/zipp425/synthwavePunk/resolve/main/synthwavePunk_v2.ckpt",
        default_image_size=512,
    ),
    ModelConfig(
        description="Graphic Art", #No
        short_name="graphic-art",
        config_path="configs/graphicArt_graphicArtBeta.yaml",
        weights_url="https://fakewebsite.com/models/graphicArt_graphicArtBeta11.safetensors",
        default_image_size=768,
    ),
    ModelConfig(
        description="Realism Engine", #Yes
        short_name="realism-engine",
        config_path="configs/realismEngine_v10.yaml",
        weights_url="https://fakewebsite.com/models/realismEngine_v10.safetensors",
        default_image_size=768,
    ),
    ModelConfig(
        description="Deliberate", #Yes
        short_name="deliberate",
        config_path="configs/stable-diffusion-v1.yaml",
        weights_url="https://fakewebsite.com/models/deliberate_v2.safetensors",
        default_image_size=512,
    ),
    ModelConfig(
        description="Deliberate Inpainting",
        short_name="deliberate-inpainting",
        config_path="configs/stable-diffusion-v1-inpaint.yaml",
        weights_url="https://fakewebsite.com/models/Deliberate-inpainting.safetensors",
        default_image_size=512,
    ),
    ModelConfig(
        description="Dreamshaper", #Try again
        short_name="dreamshaper",
        config_path="configs/stable-diffusion-v1.yaml",
        weights_url="https://fakewebsite.com/models/dreamshaper_5BakedVae.safetensors",
        default_image_size=512,
    ),
    ModelConfig(
        description="Neurogen", #No
        short_name="neurogen",
        config_path="configs/stable-diffusion-v1.yaml",
        weights_url="https://fakewebsite.com/models/neurogenV11_v11.safetensors",
        default_image_size=512,
    ),
    ModelConfig(
        description="Neverending Dream", #Try again
        short_name="neverending-dream",
        config_path="configs/stable-diffusion-v1.yaml",
        weights_url="https://fakewebsite.com/models/neverendingDreamNED_bakedVae.safetensors",
        default_image_size=512,
    ),
    ModelConfig(
        description="Realistic Vision", #Yes
        short_name="realistic-vision",
        config_path="configs/stable-diffusion-v1.yaml",
        weights_url="https://fakewebsite.com/models/realisticVisionV20_v20.safetensors",
        default_image_size=512,
    ),
    ModelConfig(
        description="Anime pastel dream", #Yes
        short_name="anime-pastel-dream",
        config_path="configs/stable-diffusion-v1.yaml",
        weights_url="https://fakewebsite.com/models/animePastelDream_hardBakedVae.safetensors",
        default_image_size=512,
    ),
]

MODEL_CONFIG_SHORTCUTS = {m.short_name: m for m in MODEL_CONFIGS}
for m in MODEL_CONFIGS:
    if m.alias:
        MODEL_CONFIG_SHORTCUTS[m.alias] = m

MODEL_CONFIG_SHORTCUTS["openjourney"] = MODEL_CONFIG_SHORTCUTS["openjourney-v2"]
MODEL_CONFIG_SHORTCUTS["oj"] = MODEL_CONFIG_SHORTCUTS["openjourney-v2"]

MODEL_SHORT_NAMES = sorted(MODEL_CONFIG_SHORTCUTS.keys())


@dataclass
class ControlNetConfig:
    short_name: str
    control_type: str
    config_path: str
    weights_url: str
    alias: str = None


CONTROLNET_CONFIGS = [
    ControlNetConfig(
        short_name="canny15",
        control_type="canny",
        config_path="configs/control-net-v15.yaml",
        weights_url="https://huggingface.co/imaginairy/controlnet/resolve/df27095611818a31c20046e10a3617c66df717b0/controlnet15_diff_canny.safetensors",
        alias="canny",
    ),
    ControlNetConfig(
        short_name="depth15",
        control_type="depth",
        config_path="configs/control-net-v15.yaml",
        weights_url="https://huggingface.co/imaginairy/controlnet/resolve/df27095611818a31c20046e10a3617c66df717b0/controlnet15_diff_depth.safetensors",
        alias="depth",
    ),
    ControlNetConfig(
        short_name="normal15",
        control_type="normal",
        config_path="configs/control-net-v15.yaml",
        weights_url="https://huggingface.co/imaginairy/controlnet/resolve/7f591ca101c550e94eb6c221b0b71915a247f244/controlnet15_diff_normal.safetensors",
        alias="normal",
    ),
    ControlNetConfig(
        short_name="hed15",
        control_type="hed",
        config_path="configs/control-net-v15.yaml",
        weights_url="https://huggingface.co/imaginairy/controlnet/resolve/df27095611818a31c20046e10a3617c66df717b0/controlnet15_diff_hed.safetensors",
        alias="hed",
    ),
    ControlNetConfig(
        short_name="openpose15",
        control_type="openpose",
        config_path="configs/control-net-v15.yaml",
        weights_url="https://huggingface.co/imaginairy/controlnet/resolve/7f591ca101c550e94eb6c221b0b71915a247f244/controlnet15_diff_openpose.safetensors",
        alias="openpose",
    ),
]

CONTROLNET_CONFIG_SHORTCUTS = {m.short_name: m for m in CONTROLNET_CONFIGS}
for m in CONTROLNET_CONFIGS:
    if m.alias:
        CONTROLNET_CONFIG_SHORTCUTS[m.alias] = m


SAMPLER_TYPE_OPTIONS = [
    "plms",
    "ddim",
    "k_dpm_fast",
    "k_dpm_adaptive",
    "k_lms",
    "k_dpm_2",
    "k_dpm_2_a",
    "k_dpmpp_2m",
    "k_dpmpp_2s_a",
    "k_euler",
    "k_euler_a",
    "k_heun",
]


def get_model_config(model_name: str) -> Optional[ModelConfig]:
    if model_name in MODEL_CONFIG_SHORTCUTS:
        return MODEL_CONFIG_SHORTCUTS[model_name]
    return None


def get_control_model_config(model_name: str) -> Optional[ControlNetConfig]:
    if model_name in CONTROLNET_CONFIG_SHORTCUTS:
        return CONTROLNET_CONFIG_SHORTCUTS[model_name]
    return None
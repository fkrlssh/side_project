"""Thin wrapper around Qwen2-VL-2B-Instruct for interpreting slide images.

The model is loaded lazily (on first use) and kept as a process-wide singleton
so the 8GB VRAM budget is only spent once, not per-request.
"""

from functools import lru_cache

from app.core.config import settings

_IMAGE_PROMPT = (
    "You are helping summarize a lecture slide for a student. "
    "Describe what this image/chart/diagram shows, focusing on the information "
    "content (data, relationships, labeled parts) rather than visual style. "
    "Be concise (2-4 sentences)."
)


class VLMClient:
    def __init__(self, model_name: str = settings.vlm_model_name, device: str = settings.vlm_device):
        self._model_name = model_name
        self._device = device
        self._model = None
        self._processor = None

    def _ensure_loaded(self):
        if self._model is not None:
            return
        import torch
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

        device = self._device if torch.cuda.is_available() else "cpu"
        self._model = Qwen2VLForConditionalGeneration.from_pretrained(
            self._model_name,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map=device,
        )
        self._processor = AutoProcessor.from_pretrained(self._model_name)
        self._device = device

    def describe_image(self, image_path: str, page_text_context: str = "") -> str:
        self._ensure_loaded()
        from PIL import Image

        prompt = _IMAGE_PROMPT
        if page_text_context:
            prompt += f"\n\nSlide text for context:\n{page_text_context}"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": Image.open(image_path)},
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        text = self._processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self._processor(
            text=[text], images=[Image.open(image_path)], return_tensors="pt"
        ).to(self._device)

        output_ids = self._model.generate(**inputs, max_new_tokens=128)
        generated = output_ids[:, inputs["input_ids"].shape[1]:]
        return self._processor.batch_decode(
            generated, skip_special_tokens=True, clean_up_tokenization_spaces=True
        )[0].strip()


@lru_cache(maxsize=1)
def get_vlm_client() -> VLMClient:
    return VLMClient()

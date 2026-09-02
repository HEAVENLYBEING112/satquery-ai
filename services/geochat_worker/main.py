import os
import io
import base64
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from PIL import Image

app = FastAPI(title="GeoChat Remote Worker")

# Global Cache
model = None
tokenizer = None
image_processor = None
model_id = "MBZUAI/GeoChat-7B"

class GeoChatRequest(BaseModel):
    query: str
    task: str # "vqa" or "grounding"
    image_base64: str

class GeoChatResponse(BaseModel):
    status: str
    task: str
    raw_text: str
    metadata: Dict[str, Any]

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "model": model_id
    }

def load_geochat():
    global model, tokenizer, image_processor
    if model is not None:
        return

    # Official GeoChat loader
    from geochat.model.builder import load_pretrained_model

    # Use 4-bit NF4
    tokenizer, model, image_processor, _ = load_pretrained_model(
        model_id,
        model_base=None,
        model_name="geochat",
        load_4bit=True
    )

@app.post("/generate", response_model=GeoChatResponse)
def generate(req: GeoChatRequest):
    if req.task not in ["vqa", "grounding"]:
        raise HTTPException(status_code=400, detail="task must be 'vqa' or 'grounding'")

    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="query must be non-empty")

    if not req.image_base64:
        raise HTTPException(status_code=400, detail="image_base64 must be non-empty")

    try:
        image_data = base64.b64decode(req.image_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="image_base64 is malformed")

    try:
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="decoded payload must be a valid image")

    try:
        load_geochat()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load GeoChat: {str(e)}")

    try:
        from geochat.conversation import conv_templates
        from geochat.constants import DEFAULT_IMAGE_TOKEN
        from geochat.mm_utils import tokenizer_image_token
        import torch

        # Preprocess using exact parameters
        image_tensor = image_processor.preprocess(image, crop_size={"height": 504, "width": 504}, size={"shortest_edge": 504}, return_tensors='pt')['pixel_values'][0]

        qs = req.query.strip()

        # Handle grounding token
        if req.task == "grounding":
            if "[grounding]" not in qs.lower():
                qs = f"[grounding] {qs}"

        qs = DEFAULT_IMAGE_TOKEN + '\n' + qs

        conv = conv_templates["llava_v1"].copy()
        conv.append_message(conv.roles[0], qs)
        conv.append_message(conv.roles[1], None)
        prompt = conv.get_prompt()

        device = model.device

        input_ids = tokenizer_image_token(prompt, tokenizer, return_tensors='pt').unsqueeze(0).to(device)
        image_tensor = image_tensor.unsqueeze(0).half().to(device)

        with torch.inference_mode():
            output_ids = model.generate(
                input_ids,
                images=image_tensor,
                do_sample=False,
                temperature=0.0,
                max_new_tokens=128
            )

        input_token_len = input_ids.shape[1]
        outputs = tokenizer.batch_decode(output_ids[:, input_token_len:], skip_special_tokens=True)[0]
        outputs = outputs.strip()

        return GeoChatResponse(
            status="success",
            task=req.task,
            raw_text=outputs,
            metadata={"model": model_id}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

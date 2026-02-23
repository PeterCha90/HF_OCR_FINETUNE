import os
import io
import json
from google.cloud import vision
from google.protobuf.json_format import MessageToDict

# 1. 서비스 계정 인증 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ocr-key.json"

# 2. Vision API 클라이언트 생성
client = vision.ImageAnnotatorClient()

def process_ocr(image_path):
    print(f"Processing {image_path}...")
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    
    image = vision.Image(content=content)
    
    # 문서 텍스트 감지 (손글씨 및 영수증 등에 더 적합)
    response = client.document_text_detection(image=image)
    
    if response.error.message:
        raise Exception(f"{response.error.message}")
    
    full_text = ""
    if response.text_annotations:
        full_text = response.text_annotations[0].description
    
    return full_text

def main():
    image_dir = "dataset/images"
    output_dir = "dataset/jsonl"
    
    # 5개의 이미지 처리
    target_images = ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg"]
    
    results = []
    
    for img_name in target_images:
        img_path = os.path.join(image_dir, img_name)
        if not os.path.exists(img_path):
            print(f"Warning: {img_path} not found.")
            continue
            
        try:
            extracted_text = process_ocr(img_path)
            
            # format.jsonl 형식을 참고하여 데이터 구성
            # image_url은 dataset/images 기준 상대 경로 또는 요구된 형식에 따름
            # 여기서는 ./images/파일명 형식으로 작성
            data = {
                "image_info": [
                    {"matched_text_index": 0, "image_url": f"./images/{img_name}"}
                ],
                "text_info": [
                    {"text": "OCR:", "tag": "mask"},
                    {"text": extracted_text, "tag": "no_mask"}
                ]
            }
            results.append(data)
        except Exception as e:
            print(f"Error processing {img_name}: {e}")

    # 결과 저장
    output_file = os.path.join(output_dir, "results.jsonl")
    with open(output_file, "w", encoding="utf-8") as f:
        for item in results:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            
    print(f"\nDone! Results saved to {output_file}")

if __name__ == "__main__":
    main()

from flask import Blueprint, request, jsonify, send_file, make_response
import io
import os
import ast
from zipfile import ZipFile

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image

bp = Blueprint('artist', __name__, url_prefix='/')

# 모델 불러오기
checkpoint_path = os.path.join(os.path.dirname(__file__), '..', 'artist_prediction/final_model_checkpoint.pt')
checkpoint = torch.load(checkpoint_path, map_location=torch.device('cpu'))
model = models.resnet50(pretrained=False)
num_ftrs = model.fc.in_features
model.fc = nn.Sequential(
    nn.Linear(num_ftrs, 1024),
    nn.Linear(1024, 25)
)
model.load_state_dict(checkpoint['net2'])
model.eval()

# 인덱스와 클래스명 매핑
index_path = os.path.join(os.path.dirname(__file__), '..', 'artist_prediction/labels.txt')

with open(index_path, 'r', encoding="UTF-8") as f:
    file_content = f.read()

dict_data = ast.literal_eval(file_content)
# print("dict data 확인", dict_data, type(dict_data))

# 아티스트 이미지 파일이 저장된 디렉토리
image_directory = os.path.join(os.path.dirname(__file__), '..', 'artist_prediction\db')

def transform_image(image_bytes):
    transform = transforms.Compose([transforms.Resize(255),
                               transforms.CenterCrop(224),
                               transforms.ToTensor(),
                               transforms.Normalize(
                                   [0.485, 0.456, 0.406],
                                   [0.229, 0.224, 0.225])])
    image = Image.open(io.BytesIO(image_bytes))
    image = transform(image).unsqueeze(0)
    return image

def get_prediction(image_bytes):
    tensor = transform_image(image_bytes)
    outputs = model.forward(tensor)
    # print("test",outputs.max(1))
    _, y_hat = outputs.max(1)
    predicted_idx = y_hat.item()
    return dict_data[predicted_idx]

# transform_image 메소드 테스트
# img_path = os.path.join(os.path.dirname(__file__), '..', 'dataset/Bike_1.jpg')
# with open(img_path, 'rb') as f:
#     image_bytes = f.read()
#     tensor = transform_image(image_bytes)
#     print(tensor)

# 업로드된 작품 아티스트 예측
@bp.route('/artist', methods=['POST'])
def classify_artist():
    if request.method == 'POST':
        file = request.files['file']
        img_bytes = file.read()
        class_name = get_prediction(img_bytes)
        return jsonify({"class_name": class_name})

# 요청 받은 아티스트 작품 이미지 전달
@bp.route('/artworks', methods=['GET'])
def zip_artwork_imgs():
    # HTTP GET 요청에서 전달된 쿼리 파라미터 받기
    args = request.args
    artist = args.get('artist')
    directory_path = os.path.join(image_directory, artist)
    exclude_filename = artist + '.jpg'
    img_names = [f for f in os.listdir(directory_path) if f != exclude_filename]

    # 압축된 ZIP 파일을 저장할 메모리 버퍼 생성
    zip_buffer = io.BytesIO()

    # ZIP 아카이브 생성
    with ZipFile(zip_buffer, 'w') as zip_archive:
        for img in img_names:
            img_path = os.path.join(directory_path, img)
            zip_archive.write(img_path, os.path.basename(img_path))

    zip_buffer.seek(0)
    response = make_response(zip_buffer.read())
    response.headers['Content-Type'] = 'application/zip'
    response.headers['Content-Disposition'] = 'attachment; filename=artworks.zip'

    return response
    # img_path = os.path.join(directory_path, img_names[0])
    # return send_file(img_path, mimetype='image/jpeg')
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from search import search_images

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    # Retrieve form data
    text_query = request.form.get('text_query', '')
    hybrid_query_weight = float(request.form.get('lam', 0.8))
    query_type = request.form.get('query_type', 'image_query')

    # Retrieve the uploaded file (if any)
    image_file = request.files.get('image_query', None)

    # If an image was uploaded, save it temporarily
    image_query_path = None
    if image_file:
        uploads_dir = os.path.join(app.instance_path, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        image_query_path = os.path.join(uploads_dir, image_file.filename)
        image_file.save(image_query_path)

    # Run the experiment with the provided parameters
    # Now search_images returns a list of (image_path, similarity_score)
    results = search_images(image_query_path, text_query, hybrid_query_weight, query_type)

    # Format the results for JSON response
    json_results = []
    for (img_path, score) in results:
        if os.path.exists(img_path):
            json_results.append({
                "image_path": img_path,
                "similarity_score": score
            })

    return jsonify({
        "results": json_results
    })

@app.route('/coco_images_resized/<filename>')
def coco_image(filename):
    return send_from_directory('coco_images_resized', filename)

if __name__ == '__main__':
    app.run(debug=True)
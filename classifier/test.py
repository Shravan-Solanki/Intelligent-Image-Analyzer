import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
import requests
import time

try:
    custom_model = tf.keras.models.load_model("sigmoid_model.keras")
except:
    print("Custom model missing.")

general_model = MobileNetV2(weights='imagenet')

def get_wikipedia_summary(query):
    formatted_title = query.replace(" ", "_")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_title}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=5)
        
            if response.status_code == 200:
                data = response.json()
                if 'extract' in data:
                    summary = data['extract']
                    sentences = summary.split('. ')
                    if len(sentences) > 1:
                        return sentences[0] + '. ' + sentences[1] + '.'
                    return summary + "."
                
            elif response.status_code == 404:
                return f"No Wikipedia page found for '{query}'."

        except requests.exceptions.RequestException:
            time.sleep(1)
            continue
            
    return "Info unavailable (Network timed out after 3 tries)."

def get_mobilenet_top_objects(img_pre, top_k=5, threshold=0.10):
    preds = general_model.predict(img_pre, verbose=0)
    decoded_list = decode_predictions(preds, top=top_k)[0]
    
    found_objects = []
    print(f"    MobileNet Raw Top {top_k}:")
    
    for i, (id, label, score) in enumerate(decoded_list):
        clean_label = label.replace("_", " ").capitalize()
        print(f"      {i+1}. {clean_label} ({score*100:.1f}%)")
        
        if score > threshold:
            found_objects.append(clean_label)
            
    return found_objects

def analyze_image(image_path):
    filename = image_path.replace("\\", "/").split("/")[-1]
    
    print(f"\n" + "="*40)
    print(f" ANALYSIS REPORT: {filename}")
    print("="*40)
    
    try:
        img = tf.keras.utils.load_img(image_path)
        img_array = tf.keras.utils.img_to_array(img)
        img_array = tf.image.resize_with_pad(img_array, 224, 224)
        img_pre = preprocess_input(tf.expand_dims(img_array, axis=0))
    except Exception as e:
        print(f" Image Load Error: {e}")
        return

    final_detected_items = []

    if  custom_model:
        preds = custom_model.predict(img_pre, verbose=0)[0]
        score_human = preds[1]
        
        print(f"\n CUSTOM MODEL CONFIDENCE:")
        print(f"    Animal: {preds[0]*100:.2f}%")
        print(f"    Human:  {preds[1]*100:.2f}%")
        print(f"    Other:  {preds[2]*100:.2f}%")
        print("-" * 20)
        
        if score_human > 0.10:
            final_detected_items.append("Human")

    print("\n Running MobileNetV2 (Scanning for details)...")
    mobilenet_objects = get_mobilenet_top_objects(img_pre, top_k=5, threshold=0.5)
    
    if mobilenet_objects:
        final_detected_items.extend(mobilenet_objects)

    final_detected_items = list(set(final_detected_items))

    if not final_detected_items:
        return

    print(f"\n Fetching definitions from Wikipedia API...")
    print("\n FINAL RESULTS:")
    print("-" * 30)
    
    for item in final_detected_items:
        definition = get_wikipedia_summary(item)
        print(f"    {item.upper()}: {definition}\n")
        
    print("="*40 + "\n")

analyze_image(r"C:\Users\HP\Downloads\human_and_dog.jpeg")
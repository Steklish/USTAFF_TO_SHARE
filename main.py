from flask import Flask, render_template, request, jsonify
import src.ustaff as ustaff_src

app = Flask(__name__)
ustaff = ustaff_src.ustaff()
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def get_bot_response():
    user_input = request.form["msg"]
    response = str(user_input)
    return jsonify({"response": response})

@app.route("/api/get-recipe", methods=["POST"])
def get_recipe():
    try:
        data = request.get_json()
        message = data.get('message', '')
        if not message:
            return jsonify({"data": "No message provided"}), 400
        
        response = ustaff.get_contextual_response(message)
        meta_info = ustaff.prev_sources
        # response = "resp"
        # meta_info = "meta"
        # Add recipe processing logic here
        return jsonify({
            "data": response,
            "metadata": meta_info
        })
    except Exception as e:
        return jsonify({
            "data": "Error occurred",
            "metadata": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)

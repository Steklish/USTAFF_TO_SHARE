import datetime
import time
from flask import Flask, Response, render_template, request, jsonify, stream_with_context
import os
import src.ustaff as ustaff_src
import src.env as env
from src.colors import *

app = Flask(__name__)
# print_directory(env.DATABASE_PATH)
ustaff = ustaff_src.ustaff()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def get_bot_response():
    user_input = request.form["msg"]
    response = str(user_input)
    return jsonify({"response": response})



@app.route("/api/get_last_message_meta", methods=["GET"])
def get_last_message_meta():
    print(YELLOW, "meta requested", RESET)
    print(YELLOW, ustaff.prev_sources, RESET)
    return jsonify({
        "metadata": ustaff.prev_sources
        # "metadata": "tetstatsdfasgdsghsjkf;"
    })

# @app.route("/api/get_response", methods=["POST"])
# def test_stream():
#     def generate_test_data():
#         # Stream 5 chunks with 0.5s delay between them
#         chunks = [
#             "This __is__ chunk 1\n",
#             """# This 
#             ```
#             asd
#             asd
#             asd
#             ```
            
#             is `chunk` 2\n""",
#             "This is *chunk* 3\n",
#             "This is chunk 4\n",
#             "This is the final chunk!"
#         ]
        
#         for chunk in chunks:
#             print(chunk)
#             yield chunk.encode('utf-8')  # Must encode to bytes
#             time.sleep(0.5)  # Simulate processing delay

#     return Response(
#         stream_with_context(generate_test_data()),
#         mimetype='text/plain',
#         headers={
#             'Cache-Control': 'no-cache',
#             'Connection': 'keep-alive'
#         }
#     )

@app.route("/api/get_response", methods=["POST"])
def get_response():
    try:
        data = request.get_json()
        message = data.get('message', '')
        if not message:
            return jsonify({"data": "No message provided"}), 400
        
        response_generator = ustaff.get_contextual_response_stream(message)
        
        @stream_with_context
        def generate():
            try:
                for chunk in response_generator:
                    # Convert ALL chunks to bytes with explicit encoding
                    if isinstance(chunk, str):
                        yield chunk.encode('utf-8')
                        time.sleep(0.08)
                    elif isinstance(chunk, bytes):
                        # Ensure bytes are UTF-8
                        try:
                            decoded = chunk.decode('utf-8').encode('utf-8')
                            yield decoded
                        except UnicodeError:
                            yield b'[BINARY DATA OMITTED]'
                    else:
                        yield str(chunk).encode('utf-8')
            except Exception as e:
                # Handle streaming errors gracefully
                yield f"\nSTREAM ERROR: {str(e)}".encode('utf-8')
        
        return Response(
            generate(),
            mimetype='text/plain',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
        )
        
    except Exception as e:
        # This catches pre-streaming errors
        return jsonify({
            "data": "Initialization error",
            "metadata": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        debug=False, 
        host="0.0.0.0", 
        port=5000,
    )

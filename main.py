import logging

from app.src import create_app


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    app = create_app()
    app.app_context().push()
    app.run(host="0.0.0.0", port=8000)
    # app.run(debug=True)

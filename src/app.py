from server import create_app

# Create the application instance using the factory
app = create_app()

if __name__ == '__main__':
    # Debug=True enables auto-reloading and detailed error pages during development
    # Use host='0.0.0.0' to make it accessible on your network (optional)
    app.run(
        debug=True,
        port=8999
    )
from aiohttp import web
import aiohttp_cors
from ai_service.routes import offer

app = web.Application()

# Setup CORS
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})
cors.add(app.router.add_post("/offer", offer))

if __name__ == "__main__":
    print("🚀 Python AI service running at http://localhost:8080")
    web.run_app(app, port=8080)

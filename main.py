from fastapi import FastAPI
import uvicorn

from address.address_book import router as address_router

app = FastAPI(title="Address Book App",
              version="0.0.1")


# root url
@app.get("/")
async def root():
    return {"message": "Hello and Welcome from Address Book API :)"}


# including the address router we have created just like blueprint
app.include_router(address_router)

# Entry point of our application to run
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=59001)

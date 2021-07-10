import lin

lin.init()
app = lin.asgi()

if __name__ == "__main__":
    lin.run("main:app")

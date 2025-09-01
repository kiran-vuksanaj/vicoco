from Xsi_Loader import Xsi_Loader


if __name__ == "__main__":

    """ silly little launcher of xsi direct """
    
    xsiHandler = Xsi_Loader()

    xsiHandler.open_handle(None,"test.wdb")

    print("status:", xsiHandler.get_status())
    clock_port = xsiHandler.get_port_number("clk")
    count_port = xsiHandler.get_port_number("count_temp")
    print("Clock:", clock_port)
    print("Count tmp:",count_port)

    xsiHandler.put_value(clock_port,0)
    xsiHandler.run(5000)

    xsiHandler.put_value(clock_port,1)
    xsiHandler.run(5000)

    print("status:", xsiHandler.get_status())

    xsiHandler.put_value(clock_port,0)
    xsiHandler.run(5000)

    xsiHandler.put_value(clock_port,1)
    xsiHandler.run(5000)
    print("hi")
    print("Clock VALUE:", xsiHandler.get_value(clock_port))

    print("status:", xsiHandler.get_status())

    xsiHandler.close()
    print("done")



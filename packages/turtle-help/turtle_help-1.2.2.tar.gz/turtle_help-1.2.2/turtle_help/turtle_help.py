import turtle as t
__version__="1.3.8"     #first version of turtle_help,it can do some easy drawing work
def draw(foot=100,color="black",bgcolor="white",shape="turtle",mode="forward",speed=1):
	"""foot:how long
           color:the color of the pen
           bgcolor:the color of the board
           shape:shape of the pen
           mode:forward or backward
           speed:speed of pen
        """
	t.speed(speed)
	t.penup()
	t.goto(0,0)
	t.pendown()
	t.pencolor(color)
	t.bgcolor(bgcolor)
	t.shape(shape)
	if mode=="forward":
		t.forward(foot)
	elif mode=="backward":
		t.backward(foot)
def circle(radius=50,color="black",bgcolor="white",shape="turtle",speed=1):
	"""radius:radius of the circle
           color:the color of the pen
           bgcolor:the color of the board
           shape:shape of the pen
           mode:forward or backward
           speed:speed of pen
        """
	t.speed(speed)
	t.penup()
	t.goto(0,0)
	t.pendown()
	t.pencolor(color)
	t.bgcolor(bgcolor)
	t.shape(shape)
	t.circle(radius)
def square_left_turn(foot=100,color="black",bgcolor="white",shape="turtle",speed=1):
	"""foot:how long
           color:the color of the pen
           bgcolor:the color of the board
           shape:shape of the pen
           mode:forward or backward
           speed:speed of pen
        """
	t.speed(speed)
	t.penup()
	t.goto(0,0)
	t.pendown()
	t.pencolor(color)
	t.bgcolor(bgcolor)
	t.shape(shape)
	t.forward(foot/2)
	t.left(90)
	t.forward(foot)
	t.left(90)
	t.forward(foot)
	t.left(90)
	t.forward(foot)
	t.left(90)
	t.forward(foot/2)
def square_right_turn(foot=100,color="black",bgcolor="white",shape="turtle",speed=1):
	"""foot:how long
           color:the color of the pen
           bgcolor:the color of the board
           shape:shape of the pen
           mode:forward or backward
           speed:speed of pen
        """
	t.speed(speed)
	t.penup()
	t.goto(0,0)
	t.pendown()
	t.pencolor(color)
	t.bgcolor(bgcolor)
	t.shape(shape)
	t.forward(foot/2)
	t.right(90)
	t.forward(foot)
	t.right(90)
	t.forward(foot)
	t.right(90)
	t.forward(foot)
	t.right(90)
	t.forward(foot/2)
def rectangle_left_turn(long=100,wide=50,color="black",bgcolor="white",shape="turtle",speed=1):
	"""long:long of the rectangle
           wide:wide of the rectangle
           color:the color of the pen
           bgcolor:the color of the board
           shape:shape of the pen
           mode:forward or backward
           speed:speed of pen
        """
	t.speed(speed)
	t.penup()
	t.goto(0,0)
	t.pendown()
	t.pencolor(color)
	t.bgcolor(bgcolor)
	t.shape(shape)
	t.forward(long/2)
	t.left(90)
	t.forward(wide)
	t.left(90)
	t.forward(long)
	t.left(90)
	t.forward(wide)
	t.left(90)
	t.forward(long/2)
def rectangle_right_turn(long=100,wide=50,color="black",bgcolor="white",shape="turtle",speed=1):
	"""long:long of the rectangle
           wide:wide of the rectangle
           color:the color of the pen
           bgcolor:the color of the board
           shape:shape of the pen
           mode:forward or backward
           speed:speed of pen
        """
	t.speed(speed)
	t.penup()
	t.goto(0,0)
	t.pendown()
	t.pencolor(color)
	t.bgcolor(bgcolor)
	t.shape(shape)
	t.forward(long/2)
	t.right(90)
	t.forward(wide)
	t.right(90)
	t.forward(long)
	t.right(90)
	t.forward(wide)
	t.right(90)
	t.forward(long/2)
def pentagon_right_turn(foot=100,color="black",bgcolor="white",shape="turtle",speed=1):
	"""foot:how long
           color:the color of the pen
           bgcolor:the color of the board
           shape:shape of the pen
           mode:forward or backward
           speed:speed of pen
        """
	t.speed(speed)
	t.penup()
	t.goto(0,0)
	t.pendown()
	t.pencolor(color)
	t.bgcolor(bgcolor)
	t.shape(shape)
	t.right(144)
	t.forward(foot)
	t.right(144)
	t.forward(foot)
	t.right(144)
	t.forward(foot)
	t.right(144)
	t.forward(foot)
	t.right(144)
	t.forward(foot)
def pentagon_left_turn(foot=100,color="black",bgcolor="white",shape="turtle",speed=1):
	"""foot:how long
           color:the color of the pen
           bgcolor:the color of the board
           shape:shape of the pen
           mode:forward or backward
           speed:speed of pen
        """
	t.speed(speed)
	t.penup()
	t.goto(0,0)
	t.pendown()
	t.pencolor(color)
	t.bgcolor(bgcolor)
	t.shape(shape)
	t.left(144)
	t.forward(foot)
	t.left(144)
	t.forward(foot)
	t.left(144)
	t.forward(foot)
	t.left(144)
	t.forward(foot)
	t.left(144)
	t.forward(foot)
def close(wait_second=0,mode="close"):
    """wait_second,how long do I wait for close the window
       mode:mode(close/done/exitonclick/wait)
    """
    import time as ti
    ti.sleep(wait_second)
    if mode=="close":
        t.bye()
    elif mode=="done":
        t.done()
    elif mode=="exitonclick":
        t.exitonclick()
    elif mode=="wait":
            import time
            time.sleep(wait_second)
def write(x=0,y=0,thing="hi!",align="left",move=False,Font_name="arial",size=50,type="normal",color="black",bgcolor="white",shape="turtle",speed=1):
    """thing--信息，将写入Turtle绘画屏幕。
       move（可选）--真/假。
       align（可选）--字符串“左(left)”、“中(center)”或“右(right)”之一。
       font（可选）--三个字体（fontname、fontsize、fonttype）。
       写入文本 - arg的字符串表示形式 - 当前
       根据“对齐”（“左”、“中”或“右”）定位乌龟以及给定的字体。
       如果move为true，则笔将移动到右下角。
       在默认情况下，move为false。
    """
    t.speed(speed)
    t.penup()
    t.goto(x,y)
    t.pendown()
    t.pencolor(color)
    t.bgcolor(bgcolor)
    t.shape(shape)
    t.write(thing,move=move,align=align,font=(Font_name,size,type))
def home():
        """go back"""
        t.speed(0)
        t.home()
def clear():
        """clear the screen"""
        t.clear()
def stamp(x=0,y=0,o_x=100,o_y=100,hide="no",shape="turtle",color="black",bgcolor="white",speed=1):
        """take a stamp"""
        t.penup()
        t.speed(speed)
        t.goto(x,y)
        t.pendown()
        t.pencolor(color)
        t.bgcolor(bgcolor)
        t.shape(shape)
        t.stamp()
        t.penup()
        t.goto(o_x,o_y)
        t.pendown()
        if hide=="yes":
            t.hideturtle()           
def draw_tree():
        """draw a tree"""
        import turtle_help_other_tree
def hide_pen():
        """hide turtle"""
        t.hideturtle()
def show_pen():
        """show turtle"""
        t.showturtle()
def pen_shape(shape="turtle",stamp="no",x=0,y=0,o_x=100,o_y=100,color="black",bgcolor="white",speed=1,hide="yes"):
    """
       take another shape
       shape:shape of pen("arrow","turtle,"circle","square","triangle","classic")
       stamp:stamp?
       …………"""
    t.shape(shape)
    t.penup()
    t.speed(speed)
    t.goto(x,y)
    t.pendown()
    t.pencolor(color)
    t.bgcolor(bgcolor)
    t.stamp()
    t.penup()
    t.goto(o_x,o_y)
    if hide=="yes":
        t.hideturtle()
def title(thing="turtle_help"):
        import turtle as t
        t.title(thing)
def other_area_count(mode="square",square_foot=10,rectangle_long=20,rectangle_wide=10,o_trangle1=10,o_trangle2=10,o_trangle3=10,trangle_foot=10,trapezium_up_long=10,trapezium_down_long=20,trapezium_high=10,circle_radius=10,circle_pi=3.1415926):
        """
           count the area
        """
        import turtle_help_other_area_count as thoac
        if mode=="square":
                S=thoac.square_area(square_foot)
                print("the area of the square is:",S)
        elif mode=="rectangle":
                S=thoac.rectangle_area(rectangle_long,rectangle_wide)
                print("the area of the rectangle is:",S)
        elif mode=="circle":
                S=thoac.circle_area(circle_pi,circle_radius)
                print("the area of the circle is:",S)
        elif mode=="trapezium":
                S=thoac.trapezium_area(trapezium_up_long,trapezium_down_long,trapezium_high)
                print("the area of the trapezium is:",S)
        elif mode=="o_trangle":
                S=thoac.o_trangle(o_trangle1,o_trangle2,o_trangle3)
                print("the area of the trangle is:",S)
def set_window(title='welcome use turtle_help!',height=600,width=800,bg_color="white"):
    """
        this function will set window,
        its height,wigth,color and title will under your contorl
    """
    t.title(title)
    t.screensize(width,height,bg_color)
if __name__ == "__main__":
        title("welcom to turtle help!")
        write(thing="WELCOME!",align="center")
        close(wait_second=5,mode="wait")
        clear()
        rectangle_right_turn()
        write(thing="CLICKME！",align="center")
        close(mode="exitonclick")
        
"""
   welcome to use turtle_help!
   this moudle just help you to use turtle moudle,it can draw a square,rectangle,circle......   
   than you for use turtle_help
                                -Dan·James·Thomas(developer)
"""

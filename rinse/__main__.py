import sys, argparse, logging
#from .classmodule import MyClass
#from .funcmodule import my_function

""" def main():
    print('in main')
    args = sys.argv[1:]
    print('count of args :: {}'.format(len(args)))
    for arg in args:
        print('passed argument :: {}'.format(arg))
    my_function('hello world')
    my_object = MyClass('Thomas')
    my_object.say_name()
if __name__ == '__main__':
    main() """

#############################

# Gather our code in a main() function
def main(args):

  # TODO Replace this with your actual code.
  print ("Let's give this a try.")
  from rpy2.rinterface import R_VERSION_BUILD
  print(R_VERSION_BUILD)

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  # TODO Specify your real parameters here.
  parser.add_argument("version",
                      help = "select version of R you would like to install.")
  args = parser.parse_args()
  
  main(args)


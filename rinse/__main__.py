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
  #logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)
  
  # TODO Replace this with your actual code.
  print ("Hello there.")
  #logging.info("You passed an argument.")
  #logging.debug("Your Argument: %s" % args.argument)
 
# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  # TODO Specify your real parameters here.
  parser.add_argument("version",
                      help = "select version of R you would like to install.")
  args = parser.parse_args()
  
  # Setup logging
  #if args.verbose:
  #  loglevel = logging.DEBUG
  #else:
  #  loglevel = logging.INFO
  
  main(args)


import extract as s1
import transform as s2
import write_to_mongoDB as s3

def main():
    try:
        s1.main()
        print("finished extraction")
    except:
        print("extraction exception")
    try:
        s2.main()
        print("finished transformation")
    except:
        print("transformation exception")
    try:
        s3.main()
        print("finished mongodb write")
    except:
        print("mongodb write exception")
    

if __name__ == "__main__":
    main()
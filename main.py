import argparse, sys, os
parser = argparse.ArgumentParser()
parser.add_argument("input_path", help="Absolute path to the input gif. The best gifs to use are small resolution gifs with 2 - 5 frames")
parser.add_argument("output_path", help="Absolute path where the output will be saved (without the output filename). If you make this parameter empty quotes then the output will be saved in the same directory as the python script.")
parser.add_argument("--makegif", action="store_true", help="Use this flag to make a gif out of the grid moving on the image")
args = parser.parse_args()

infn = args.input_path[args.input_path.rfind('\\')+1::]
mg = args.makegif
try:
    from PIL import Image, ImageDraw
except:
    print("PIL not installed. Write \"pip install Pillow\" in the console to install PIL")
    sys.exit(1)
try:
    from progress.bar import ChargingBar
except:
    print("progress not installed. Write \"pip install progress\" in the console to install progress")
    sys.exit(1)
imArr = []
def processImage(infile):
    global imArr
    try:
        im = Image.open(infile)
    except IOError:
        print ("Cant load", infile)
        sys.exit(1)
    i = 0
    mypalette = im.getpalette()

    try:
        while 1:
            im.putpalette(mypalette)
            new_im = Image.new("RGBA", im.size)
            new_im.paste(im)
            new_im = new_im.resize(tuple([2*x for x in new_im.size]), resample=Image.BOX)
            print("Processing gif frame #", i)
            imArr.append(new_im)
            i += 1
            im.seek(im.tell() + 1)

    except EOFError:
        pass # end of sequence
print("Processed all gif frames")
print("Doing magic with frames...")
processImage(args.input_path)
frames = len(imArr)
result = Image.new("RGBA", imArr[0].size)
for i in range(result.size[0]):
    fr = i%frames
    pos = (i, 0, i+1, result.size[1])
    region = imArr[fr].crop(pos)
    result.paste(region, pos)
if not mg: result.save(args.output_path + infn[:-4] + "_moirepattern.png")
print("Finished doing magic with frames")
print("Making grid...")
grid = Image.new("RGBA", result.size)
draw = ImageDraw.Draw(grid)
for i in range(grid.size[0]):
    if i % frames != 0:
        draw.line((i, 0, i, grid.size[1]), fill=(0, 0, 0))
del draw
if not mg: grid.save(args.output_path + infn[:-4] + "_moiregrid.png")
print("Finished making grid...")
if mg:
    resgifs = []
    mx = grid.size[0] + result.size[0]
    d = grid.size[0]
    with ChargingBar('Making final gif frames', max=mx, suffix='') as bar:
        for i in range(-grid.size[0], result.size[0]):
            bar.suffix = f"{bar.index + 1} / {mx}"
            temp = result.copy()
            temp.paste(grid, (i, 0, i + grid.size[0], result.size[1]), mask=grid)
            resgifs.append(temp)
            #print("Processed final gif frame #", i + d, "out of", mx)
            bar.next()
    resgifs[0].save(args.output_path + infn[:-4] + "_moire.gif",
                   save_all=True, append_images=resgifs[1:], optimize=False, duration=150)

print("Finished. The output file(s) will be saved in", (os.getcwd(), args.output_path)[bool(args.output_path)])

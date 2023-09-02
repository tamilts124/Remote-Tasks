import sys, os
from threading import Thread
from ffmpeg import FFmpeg #pip install python-ffmpeg
from ffprobe import FFProbe #pip install ffprobe-python

threads, mthreads =5, 5
sample_video_formats =['.mp4', '.webm', '.avi', '.mov']
errors ={}

def changeFramerate(videopath, savepath, framerate):
    global threads
    threads -=1
    try:
        if os.path.exists(savepath):
            sp =FFProbe(savepath).metadata
            vp =FFProbe(videopath).metadata
            if sp.get('Duration')==vp.get('Duration'):
                print(savepath+' [Done]')
                threads +=1; return
        FFmpeg().option('y').input(videopath).output(savepath, vf=f'fps={framerate}').execute()
    except Exception as e:
        print(savepath+f' [ Failed: {e}]')
        if not errors.get(e): errors[e] =[]
        errors[e].append(videopath)
    else:
        orgsize =os.path.getsize(videopath)/1024/1024 # in MB
        chgsize =os.path.getsize(savepath)/1024/1024 # in MB
        print(savepath+f' [ {orgsize:.0f}MB-{chgsize:.0f}MB ]')
    threads +=1

def main(folderpath, frames, storepath):
    if not folderpath.endswith('/'): folderpath +='/'
    foldername =folderpath.split('/')[-2]
    foldername +=' [FrameChanged]'
    if not storepath.endswith('/'): storepath +='/'
    basefolder =storepath+foldername+'/'
    if not os.path.exists(basefolder): os.makedirs(basefolder)
    for path, folders, files in os.walk(folderpath):
        path +='/'
        folder =basefolder+path.replace(folderpath, '', 1)
        if not os.path.exists(folder): os.makedirs(folder)
        for file in files:
            for vformat in sample_video_formats:
                if file.lower().endswith(vformat):
                    while threads<=0: pass
                    Thread(target=changeFramerate, args=[path+file, folder+file, frames]).start()
    while not threads==mthreads: pass
    if errors:
        print('\nFails: ')
        for error, videos in errors.items():
            print('\n', error, '\n')
            for video in videos: print(video)


if __name__ == '__main__':
    path, store, frame ='./', './', 1
    if len(sys.argv)==1 or sys.argv[1].lower() in ('-h', '--help'): print('''
    Usage: script.py <path> <frame> <store>
                    
    path - Which folder contains Videos to be Change The Framerate [require]
    frame - How Much Frame Per Second, Default "1"
    store - Where to Store After Changed, Default "./"
    '''), exit(1)
        
    if len(sys.argv)>1:
        path =sys.argv[1]
        if len(sys.argv)>2:
            frame =sys.argv[2]
            if len(sys.argv)>3: store =sys.argv[3]
    main(path, float(frame), store)

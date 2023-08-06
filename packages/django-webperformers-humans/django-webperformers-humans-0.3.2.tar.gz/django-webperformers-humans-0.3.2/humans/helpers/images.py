import logging
import pathlib
from subprocess import call
logger = logging.getLogger('django')

def resizeImage(imgPath:str):
    cmds:list = []      
    existingPath = pathlib.Path(imgPath)
    destPath = existingPath.parent
    fileName = existingPath.stem
    quality = 100
    mdWidth =  512
    smWidth = 320
    cmdLg='cwebp \"'+imgPath+'\" -q '+str(quality)+' -o '+ str(pathlib.PurePath(destPath,fileName+'_lg.webp'))
    cmdMd='cwebp \"'+imgPath+'\" -q '+str(quality)+' -resize '+str(mdWidth)+' 0 -o '+ str(pathlib.PurePath(destPath,fileName+'_md.webp'))
    cmdSm='cwebp \"'+imgPath+'\" -q '+str(quality)+' -resize '+str(smWidth)+' 0 -o '+ str(pathlib.PurePath(destPath,fileName+'_sm.webp'))

    cmds.append(cmdLg)
    cmds.append(cmdMd)
    cmds.append(cmdSm)

    for comm in cmds:
        call(comm, shell=True)
# -*- coding: utf-8 -*-

u"""
プログラミングコンテストでのテストを補助するための関数群
"""

import optparse
import tempfile
import sys
import subprocess
import os
import time

import colors

parser = optparse.OptionParser()
parser.add_option(
  '-t', '--timelimit',
  action = 'store', dest = 'timeLimit',
  type = 'string',
  metavar = 'LIMIT',
  default = '5s',
  help = 'set time limit: default = 5s'
)
parser.add_option(
  '-e', '--exe',
  action = 'store', dest = 'exeFileName',
  type = 'string',
  metavar = 'exeFILE',
  default = 'a.out',
  help = 'set executive file name'
),
parser.add_option(
  '-s', '--submit-filename',
  action = 'store', dest = 'tmpSrcFileName',
  default = 'submit.cpp',
  metavar = 'FILE',
  help = 'set submit filename'
)

parser.set_defaults(allTest = None)
parser.set_defaults(showInput = None)
parser.set_defaults(fullIO = None)
parser.set_defaults(diffRun = None)
parser.set_defaults(precise = None)
parser.set_defaults(judgeCompile = None)
parser.set_defaults(debug = None)
parser.set_defaults(extraPlaceholder = None)
parser.set_defaults(run = True)



def generateSourceFileName(fileId):
  u"""file IDに対応するソースファイル名を生成する"""
  return fileId + '.cpp'

def generateTestFileNamePrefixes(fileId):
  u"""file IDに対応するテストケースの想定prefix群を生成する"""
  return [fileId] + [fileId + str(i) for i in xrange(10)] + [fileId + '.' + str(i) for i in xrange(10)]

def generateInputFileName(prefix):
  u"""指定されたprefixを持つ入力ファイル名を生成する"""
  return prefix + '.in'

def generateAnswerFileName(prefix):
  u"""指定されたprefixを持つ回答ファイル名を生成する"""
  return prefix + '.out'

def generateTmpOutFileName():
  u"""一時ファイルを生成してそのファイル名を返す"""
  return tempfile.mkstemp()[1]

def generateTmpSrcFile(srcFileName, tmpSrcFileName):
  u"""デバッグ情報をカットした提出用の一時ファイルを生成する"""
  if( not os.path.exists(srcFileName) ):
    print( colors.strColored(srcFileName + ' is not found.', colors.RED, colors.EMP) )
    exit(-1)
  srcFile = open(srcFileName, 'r')
  if( srcFile is None ):
    print( colors.strColored(srcFileName + ' cannot open.', colors.RED, colors.EMP) )
    exit(-1)
  tmpSrcFile = open(tmpSrcFileName, 'w')
  if( tmpSrcFile is None ):
    print( colors.strColored(tmpSrcFileName + ' cannot open.', colors.RED, colors.EMP) )
    exit(-1)

  inCount = 0
  for line in srcFile:
    line = line[:line.find(r'//^@')] + '\n'
    tokens = line.split()
    if(len(tokens) == 4):
      if(tokens[0:4] == ['//', 'BEGIN', 'CUT', 'HERE']):
        inCount += 1
        continue
      if(tokens[0:4] == ['//', 'END', 'CUT', 'HERE']):
        inCount -= 1
        continue
    if(len(tokens) >= 1 and tokens[0][0:5] == 'DEBUG'):
      continue
    if(inCount == 0):
      tmpSrcFile.write(line)
    if(inCount < 0):
      print( colors.strColored('unbalance!!!!!!', colors.RED, colors.EMP) )
      exit(-1)
  if( inCount != 0 ):
    print( colors.strColored('unbalance!!!', colors.RED, colors.EMP) )
    exit(-1)
  tmpSrcFile.close()
  srcFile.close()



def changeExtraPlaceholder(tmpSrcFileName):
  u"""%lldを%I64dで置き換える(主にCodeForces用)"""
  tmpFileName = generateTmpOutFileName()
  if( subprocess.Popen(['cp', tmpSrcFileName, tmpFileName]).wait() != 0 ):
    print( colors.strColored('something failed.', colors.RED, colors.EMP) )
    exit(-1)
  tmpFile = open(tmpFileName, 'r')
  if( tmpFile is None ):
    print( colors.strColored('temp file cannot open.', colors.RED, colors.EMP) )
    exit(-1)
  tmpSrcFile = open(tmpSrcFileName, 'w')
  if( tmpSrcFile is None ):
    print( colors.strColored(tmpSrcFileName + ' cannot open.', colors.RED, colors.EMP) )
    exit(-1)

  for line in tmpFile:
    tmpSrcFile.write(line.replace('%lld', '%I64d'))
  tmpFile.close()
  tmpSrcFile.close()
  removeFile(tmpFileName)



def removeFile(fileName):
  u"""指定されたファイルを消去する"""
  return subprocess.call(['rm', fileName]) == 0



def localCompile(srcFileName, exeFileName = 'a.out'):
  u"""ソースファイルをローカル環境に合わせてコンパイルする"""
  return subprocess.call(['gpp', '-o', exeFileName, srcFileName]) == 0

def judgeCompile(srcFileName, exeFileName = 'a.out'):
  u"""ソースファイルをジャッジ環境に(なるべく)合わせてコンパイルする"""
  return subprocess.call(['g++', '-O2', '-o', exeFileName, '-Wall', '-Wextra', '-Wno-unused-result', '-DONLINE_JUDGE', srcFileName]) == 0


def copyFile(fileName):
  u"""指定されたファイルの中身をクリップボードに貼り付ける"""
  return subprocess.call(['copy', fileName]) == 0



def printSignal(signal):
  u"""signal codeに対応した異常終了の原因を出力する"""
  def printUnusualSignal(comment):
    print( colors.EMP + colors.RED + 'failed: ' + colors.YELLOW + comment + colors.CLEAR )

  if( signal != 0 ):
    if( signal == 124 ):
      printUnusualSignal('TLE: time limit exceeded.')
    elif( signal == 8 + 128 ):
      printUnusualSignal('SIGFPE: zero divide or overflow.')
    elif( signal == 11 + 128 ):
      printUnusualSignal('SIGSEGV: segmentation fault.')
    elif( signal == 6 + 128 ):
      printUnusualSignal('SIGABRT: assert or abort.')
    else:
      printUnusualSignal('signal(' + str(signal - 128) + ')')



def printTime(t):
  u"""実行時間を出力する"""
  print( colors.strColored('time: ' + ('%.4f' % t), colors.YELLOW) )



def showInput(options, inputFileName):
  u"""入力ファイルを画面に出力する"""
  showCmd = ['cat'] if options.fullIO else ['head', '-n', '4']
  showCmd.append(inputFileName)
  return subprocess.call(showCmd) == 0



def singleTest(options, inputFileName):
  u"""指定された入力ファイル名に対してプログラムを実行する"""
  startTime = time.time()
  p = subprocess.Popen(['timeout', options.timeLimit, './'+options.exeFileName],
                        stdin = open(inputFileName, 'r'),
                        stdout = sys.stdout if options.fullIO else subprocess.PIPE)
  signal = p.wait()
  endTime = time.time()
  if(not options.fullIO ):
    subprocess.Popen(['head', '-n', '4'], stdin = p.stdout).wait()
  printSignal(signal)
  printTime(endTime - startTime)



def diffTest(options, inputFileName, ansFileName):
  u"""回答ファイルが存在するときテストを実行しdiffを出力する"""
  tmpOutFileName = generateTmpOutFileName()
  startTime = time.time()
  p = subprocess.Popen(['timeout', options.timeLimit, './'+options.exeFileName],
                        stdin = open(inputFileName, 'r'),
                        stdout = open(tmpOutFileName, 'w'))
  signal = p.wait()
  endTime = time.time()
  if( signal != 0 ):
    print( colors.strColored('Your output for ' + inputFileName, colors.CYAN) )
    showCmd = ['cat'] if options.fullIO else ['head', '-n', '4']
    showCmd.append(tmpOutFileName)
    subprocess.Popen(showCmd).wait()
    printSignal(signal)
  else:
    diff(options, ansFileName, tmpOutFileName)
  printTime(endTime - startTime)
  removeFile(tmpOutFileName)



def diff(options, ansFileName, outFileName):
  u"""回答ファイルと実行結果のdiffを出力する"""
  diffProc = subprocess.Popen(['diff', '--width=40', '-y', ansFileName, outFileName], stdout = subprocess.PIPE)
  result = diffProc.wait()

  showCmd = ['cat'] if options.fullIO else ['head', '-n', '4']
  if( result == 0 ):
    print( colors.strColored('Expected == Your Output', colors.CYAN) )
    showCmd.append(outFileName)
    subprocess.Popen(showCmd).wait()
    print( '\n' + colors.strColored('Accepted!', colors.CYAN, colors.EMP) )
  else:
    print( colors.strColored('Expected  <>  Your Output', colors.CYAN) )
    subprocess.Popen(showCmd, stdin = diffProc.stdout).wait()
    if( options.precise ):
      print( '\n' +  colors.strColored('Wrong Answer.', colors.RED, colors.EMP) )
    else:
      print( '\n' +  colors.strColored('Check Yourself.', colors.MAGENTA, colors.EMP) )
  return result == 0



def compile(options, srcFileName):
  u"""ソースファイルをコンパイルする"""
  srcModifiedTime = os.stat(srcFileName).st_mtime
  exeModifiedTime = os.stat(options.exeFileName).st_mtime if os.path.exists(options.exeFileName) else -1.0
  #FIXME
  if(True or srcModifiedTime > exeModifiedTime ):
    print( colors.strColored('Compiling ...', colors.CYAN) )
    result = judgeCompile(srcFileName, options.exeFileName) if options.judgeCompile else localCompile(srcFileName, options.exeFileName)
    if( not result ):
      print( colors.strColored('Compile Failed:', colors.RED, colors.EMP) )
      exit(-1)
    else:
      print( colors.strColored('Compile Succeeded.', colors.CYAN) )
  else:
    print( colors.strColored('Compile Passed.', colors.CYAN) )



def testRun(options, prefix):
  u"""オプションに従ってテストを実行する"""
  inputFileName = generateInputFileName(prefix)
  answerFileName = generateAnswerFileName(prefix)

  #display input
  print( colors.strColored(inputFileName if options.showInput else prefix, colors.CYAN) )
  if( options.showInput ):
    showInput(options, inputFileName)

  #display output
  if( options.diffRun and os.path.exists( answerFileName ) ):
    #extra check
    if( answerFileName.lower() == options.exeFileName.lower() ):
      print( colors.strColored('Warning: Answer File == Executive File.', colors.RED, colors.EMP) )
    else:
      diffTest(options, inputFileName, answerFileName)
  else:
    if( options.showInput ):
      print( colors.strColored('Your output for ' + inputFileName, colors.CYAN) )
    singleTest(options, inputFileName)



def run(options, args):
  u"""適切なオプションの下でテストを実行する"""
  if( len(args) == 0 ):
    print( colors.strColored('No File ID.', colors.RED, colors.EMP) )
    parser.print_usage()
    exit(-1)
  fileId = args[0]
  srcFileName = generateSourceFileName(fileId)
  if( not os.path.exists(srcFileName) ):
    print( colors.strColored(srcFileName + ' is not found.', colors.RED, colors.EMP) )
    exit(-1)

  generateTmpSrcFile(srcFileName, options.tmpSrcFileName)
  compile(options, srcFileName if options.debug else options.tmpSrcFileName)

  if(options.run):
    prefixes = generateTestFileNamePrefixes(fileId) if (len(args) == 1 or options.allTest) else args[1:]
    prefixes = filter(lambda x : os.path.exists( generateInputFileName(x) ), 
                    prefixes)
    if( not (len(args) > 1 or options.allTest) ):
      prefixes = prefixes[:1]
  
    if( len(prefixes) == 0 ):
      print( colors.EMP + colors.RED + 'Warning: ' + colors.YELLOW + 'No Input File Exists.' + colors.CLEAR )
  
    print('-'*40)
    for prefix in prefixes:
      testRun(options, prefix)
      print('-'*40)

  if( options.extraPlaceholder ):
    changeExtraPlaceholder(options.tmpSrcFileName)
  copyFile(options.tmpSrcFileName)


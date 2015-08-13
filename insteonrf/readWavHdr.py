#!/usr/local/bin/python
"""
 
 Program for reading a Wav header from a data file

"""
#
# Wave header mostly lifted from 
#  http://blog.theroyweb.com/extracting-wav-file-header-information-using-a-python-script
#
import os
import stat
import struct
# import pprint


def readWavHeader(fd=None):
    """ Extracts data in the first 44 bytes in a WAV file and writes it
            out in a human-readable format
    """
    if fd is None :
        raise ValueError("arg not open file")
    # end try
    # Read in all data
    bufHeader = fd.read(38)
    # Verify that the correct identifiers are present
    if (bufHeader[0:4] != "RIFF") or \
       (bufHeader[12:16] != "fmt "): 
         raise ValueError("Input file not a standard WAV file")
    # endif
    stHeaderFields = {'ChunkSize' : 0, 'Format' : '',
        'Subchunk1Size' : 0, 'AudioFormat' : 0,
        'NumChannels' : 0, 'SampleRate' : 0,
        'ByteRate' : 0, 'BlockAlign' : 0,
        'BitsPerSample' : 0, 'Filename': '',
        'chunksList' : { } }
    # Parse fields

    stHeaderFields['fstat'] = os.fstat(fd.fileno())

    stHeaderFields['ChunkSize'] = struct.unpack('<L', bufHeader[4:8])[0]
    stHeaderFields['Format'] = bufHeader[8:12]
    # stHeaderFields['Subchunk1ID'] = bufHeader[12:16]
    stHeaderFields['Subchunk1Size'] = struct.unpack('<L', bufHeader[16:20])[0]
    stHeaderFields['AudioFormat'] = struct.unpack('<H', bufHeader[20:22])[0]
    stHeaderFields['NumChannels'] = struct.unpack('<H', bufHeader[22:24])[0]
    stHeaderFields['SampleRate'] = struct.unpack('<L', bufHeader[24:28])[0]
    stHeaderFields['ByteRate'] = struct.unpack('<L', bufHeader[28:32])[0]
    stHeaderFields['BlockAlign'] = struct.unpack('<H', bufHeader[32:34])[0]
    stHeaderFields['BitsPerSample'] = struct.unpack('<H', bufHeader[34:36])[0]

    # Locate subchunks data chunk
    chunksList = stHeaderFields['chunksList']
    dataChunkLocation = 0
    fd.seek(0, 2) # Seek to end of file
    inputFileSize = fd.tell()
    stHeaderFields['FileSize'] = inputFileSize
    nextChunkLocation = 12 # skip the RIFF header
    while 1:
        chunk = dict()
        # Read subchunk header
        fd.seek(nextChunkLocation)
        headersize = 8
        bufHeader = fd.read(headersize)

        subchunkname = bufHeader[0:4]
        subchunksize = struct.unpack('<L', bufHeader[4:8])[0]
        if subchunkname == "data":
            dataChunkLocation = nextChunkLocation
        elif subchunkname == "LIST":
            i = 0
            j = 4
            cbuff = fd.read(subchunksize)
            chunk["typeID"] =  cbuff[i:j]
            i = j

            Tags = dict()
            chunk["Tags"] = Tags
            while( (subchunksize -i) > 0 ) :
                j = j + 4
                tagn = cbuff[i:j]
                i = j ; j = i + 4
                dLen = struct.unpack('<L', cbuff[i:j])[0]
                i = j ; j = i + dLen
                Tags[tagn] = cbuff[i:j]
                i = j


        chunk["chunkID"] = subchunkname
        chunk["chunkLocation"] = nextChunkLocation
        chunk["chunkSize"] = subchunksize
        chunksList[subchunkname] = chunk

        nextChunkLocation += (headersize + subchunksize)
        if nextChunkLocation >= inputFileSize:
            break
        
    
    #stHeaderFields['Filename'] = os.path.basename(strWAVFile)
    stHeaderFields['Filename'] = fi.name

    return stHeaderFields

AudioFormatTypes = {
    0: "Unknown",
    1: "PCM/uncompressed",
    2: "Microsoft ADPCM",
    6: "ITU G.711 a-law",
    7: "ITU G.711 u-law",
    17: "IMA ADPCM",
    20: "ITU G.723 ADPCM (Yamaha)",
    49: "GSM 6.10",
    64: "ITU G.721 ADPCM",
    80: "MPEG",
    65536: "Experimental"
}

def printWavHdr(winfo) :
    # pprint.pprint(winfo)

    print winfo["Filename"], ":"

    if "fstat" in winfo :
        print "    {:<25s} : {:d}".format("File Size", winfo["fstat"][stat.ST_SIZE])

    print "    {:<25s} : {!s}".format("bitrate",
        (winfo["ByteRate"] * 8))
    print "    {:<25s} : {!s}".format("AvgBytesPerSec",
        (winfo["SampleRate"] * winfo["BlockAlign"]) )
    for k, v in winfo.items() :
        if k == "chunksList" :
            continue
        elif  k in [ "Filename", 'fstat'] :
            continue
        elif  k == "AudioFormat" :
            if v in AudioFormatTypes :
                audiotype = AudioFormatTypes[v]
            else :
                audiotype = "??"
            print "    {:<25s} : {!s} ({!s})".format(k, v, audiotype)
        elif k == 'FileSize' :
            print "    {:<25s} : {!s} ({:#X})".format(k, v, int(v))
        else :
            print "    {:<25s} : {!s}".format(k, v)

    for k, v in winfo['chunksList'].items() :
        if k == "fmt " :
            continue
        print "    ", k, ":"
        for ck, cv, in v.items() :
            if ck in ['chunkLocation', 'chunkSize'] :
                print "\t{:<21s} : {!s} ({:#X})".format(ck, cv, int(cv))
            else :
                print "\t{:<21s} : {!s}".format(ck, cv)
        if k == "data" :
            if winfo["ByteRate"] == 0 :
                data_length = "??"
            else :
                data_length = float( v["chunkSize"] / float(winfo["ByteRate"]) )

            print "\t{:<21s} : {!s} sec".format( "Length", data_length);

            # print "chunkSize", v["chunkSize"], " /  ByteRate", winfo["ByteRate"]

            sample_size =  (winfo["BitsPerSample"] >> 3) * winfo["NumChannels"]
            if sample_size == 0 :
                samples = "??"
            else :
                samples = (v["chunkSize"] / sample_size )
            print "\t{:<21s} : {!s}".format("Samples", samples)
            print "\t{:<21s} : {!s}".format("Sample_size", sample_size)
            print "\t{:<21s} : {!s}".format(
                "AvgSamplePerSec",
                (( winfo["SampleRate"] * winfo["BlockAlign"])/sample_size))

    if  'ChunkSize' in winfo and 'FileSize' in winfo :
        if winfo['ChunkSize'] > winfo['FileSize'] :
            print "Warning ChunkSize > FileSize : {!s} > {!s}".format ( 
                winfo['ChunkSize'], winfo['FileSize']);

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print "Invalid argument. Exactly one wave file location required as argument"
        exit(0)

    for fn in sys.argv[1:] :
        with open(fn, 'rb') as fi :
            winfo = readWavHeader(fi)
            printWavHdr(winfo)

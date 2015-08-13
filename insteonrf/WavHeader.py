#!/usr/local/bin/python2.7
"""
 
 This is Junk code 
 written for onetime use     
 for proof of concept
 

 WavHeader.py
   Extract basic header information from a WAV file

"""

short_print=None
 
def PrintWavHeader(strWAVFile):
    """ Extracts data in the first 44 bytes in a WAV file and writes it
            out in a human-readable format
    """
    import os
    import struct
    import logging
    logging.basicConfig(level=logging.DEBUG)
    def DumpHeaderOutput(structHeaderFields):
        for key in structHeaderFields.keys():
            print "%s: " % (key), structHeaderFields[key]
        # end for
    # Open file
    try:
        fileIn = open(strWAVFile, 'rb')
    except IOError, err:
        logging.debug("Could not open input file %s" % (strWAVFile))
        return
    # end try
    # Read in all data
    bufHeader = fileIn.read(38)
    # Verify that the correct identifiers are present
    if (bufHeader[0:4] != "RIFF") or \
       (bufHeader[12:16] != "fmt "): 
         logging.debug("Input file not a standard WAV file")
         return
    # endif
    stHeaderFields = {'ChunkSize' : 0, 'Format' : '',
        'Subchunk1Size' : 0, 'AudioFormat' : 0,
        'NumChannels' : 0, 'SampleRate' : 0,
        'ByteRate' : 0, 'BlockAlign' : 0,
        'BitsPerSample' : 0, 'Filename': ''}
    # Parse fields
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
    # Locate & read data chunk
    chunksList = []
    dataChunkLocation = 0
    fileIn.seek(0, 2) # Seek to end of file
    inputFileSize = fileIn.tell()
    nextChunkLocation = 12 # skip the RIFF header
    while 1:
        # Read subchunk header
        fileIn.seek(nextChunkLocation)
        bufHeader = fileIn.read(8)
        if bufHeader[0:4] == "data":
            dataChunkLocation = nextChunkLocation
        # endif
        subchunksize = struct.unpack('<L', bufHeader[4:8])[0]
        chunksList.append( (bufHeader[0:4], nextChunkLocation, subchunksize) )
        nextChunkLocation += (8 + struct.unpack('<L', bufHeader[4:8])[0])
        if nextChunkLocation >= inputFileSize:
            break
        # endif
    # end while
    # Dump subchunk list
    if short_print is None :
        print "Subchunks Found: "
        for chunkName in chunksList:
            print "%s:%d:%d, " % (chunkName[0], chunkName[1], chunkName[2]),
        # end for
        print "\n"
    # Dump data chunk information
    if dataChunkLocation != 0:
        fileIn.seek(dataChunkLocation)
        if short_print is None : 
            bufHeader = fileIn.read(8)
            print "Data Chunk located at offset [%s] of data length [%s] bytes" % \
                (dataChunkLocation, struct.unpack('<L', bufHeader[4:8])[0])
            stHeaderFields['Filename'] = os.path.basename(strWAVFile)
            DumpHeaderOutput(stHeaderFields)
        else :
            print os.path.basename(strWAVFile), ":",
            for v in [ "ByteRate", "BitsPerSample", "SampleRate" ] :
                if v in stHeaderFields :
                    print stHeaderFields[v],
            print


    # Close file
    fileIn.close()
 
if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if args[0] == "-s" :
        short_print=1
        args.pop(0)

    if len(args) < 0:
        print "Invalid argument. wave file location required as argument"
    else:
        for f in args :
            PrintWavHeader(f)

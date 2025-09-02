import math

from struct import unpack,pack
from random import randint

from time import perf_counter_ns
start_time = perf_counter_ns()

class config:

    image_target = "temp_test_bmp_image.bmp"


    audio_resolution = 2                #possibe values: 1,2,4
    sample_rate = 20000
    audio_length = 2
    sample_number = audio_length *sample_rate


    def populate_config():
        config_file = open("settings.txt","r")
        config_text = config_file.readlines()
        config_file.close()

        config_list = []

        #for i,text in enumerate(config_text):

        for text in config_text:
            if ":" in text:
                text.find("\n")
                config_list.append([text[0:text.find(":")],text[text.find(":")+1 :text.find("\n")]])

        

        print(config_list)





        return()

config.populate_config()





#--------------------------------------------------------------------------------------------------------------
class dib_header_decoding:
    dib_header_type = ""
    image_width = 0
    image_height = 0
    number_of_color_planes = 1          #should allways be 1
    bits_per_pixel = 0
    compression_method = 0              # beyond 0 (none) I'l mabe do 1 (RLE-8) and 2 (RLE-4); Right now i can't be bothered with the rest
    image_size = 0
    resolution_horizontal = 0
    resolution_vertical = 0
    palette_color_number = 0
    number_of_important_colors = 0
    has_alpha = True

    def get_info_from_BITMAPCOREHEADER(bmp:bytes):
        dib_header_decoding.image_width = int.from_bytes(bmp[18:20], byteorder="little")
        dib_header_decoding.image_height = int.from_bytes(bmp[20:22], byteorder="little")
        dib_header_decoding.number_of_color_planes = int.from_bytes(bmp[22:24], byteorder="little")
        dib_header_decoding.bits_per_pixel = int.from_bytes(bmp[24:26], byteorder="little")

        dib_header_decoding.palette_color_number = 2**dib_header_decoding.bits_per_pixel
        if (dib_header_decoding.bits_per_pixel/8)%4 == 0:
            dib_header_decoding.has_alpha == True
        elif (dib_header_decoding.bits_per_pixel/8)%3 == 0:
            dib_header_decoding.has_alpha = False
        return()

    def get_info_from_BITMAPINFOHEADER(bmp:bytes):
        dib_header_decoding.image_width = int.from_bytes(bmp[18:22], byteorder="little",signed=True)
        dib_header_decoding.image_height = int.from_bytes(bmp[22:26], byteorder="little",signed=True)
        dib_header_decoding.number_of_color_planes = int.from_bytes(bmp[26:28], byteorder="little")
        dib_header_decoding.bits_per_pixel = int.from_bytes(bmp[28:30], byteorder="little")
        dib_header_decoding.compression_method = int.from_bytes(bmp[30:34], byteorder="little")
        dib_header_decoding.image_size = int.from_bytes(bmp[34:38], byteorder="little")
        dib_header_decoding.resolution_horizontal = int.from_bytes(bmp[38:42], byteorder="little",signed=True)
        dib_header_decoding.resolution_vertical = int.from_bytes(bmp[42:46], byteorder="little",signed=True)
        dib_header_decoding.palette_color_number = int.from_bytes(bmp[46:50], byteorder="little")
        dib_header_decoding.number_of_important_colors = int.from_bytes(bmp[50:54], byteorder="little")

        if dib_header_decoding.palette_color_number == 0:
            dib_header_decoding.palette_color_number = 2**dib_header_decoding.bits_per_pixel
        if (dib_header_decoding.bits_per_pixel/8)%4 == 0:
            dib_header_decoding.has_alpha == True
        elif (dib_header_decoding.bits_per_pixel/8)%3 == 0:
            dib_header_decoding.has_alpha = False

        
        return()

    def print_header_info():
        print("-------------------------------------------------------")
        print(f"DIB header type:{dib_header_decoding.dib_header_type}")
        print(f"width:{dib_header_decoding.image_width}")
        print(f"height:{dib_header_decoding.image_height}")
        print(f"color plane number:{dib_header_decoding.number_of_color_planes}")
        print(f"bits per pixel:{dib_header_decoding.bits_per_pixel}")
        print(f"compression method:{dib_header_decoding.compression_method}")
        print(f"image size:{dib_header_decoding.image_size}")
        print(f"horizontal resolution:{dib_header_decoding.resolution_horizontal}")
        print(f"vertical resolution:{dib_header_decoding.resolution_vertical}")
        print(f"number of colors in the palette:{dib_header_decoding.palette_color_number}")
        print(f"has alpha:{dib_header_decoding.has_alpha}")        
        print(f"number of important colors:{dib_header_decoding.number_of_important_colors}")
        print("-------------------------------------------------------")

class image_processing:



    def get_image_data(name:str)->list:
        file = open(name,"rb")
        raw_file = file.read()
        file.close()

        offset = int.from_bytes(raw_file[10:14], byteorder="little")
        dib_header_size = int.from_bytes(raw_file[14:18], byteorder="little")

        match dib_header_size:
            case 12:
                dib_header_decoding.dib_header_type = "BITMAPCOREHEADER"
                dib_header_decoding.get_info_from_BITMAPCOREHEADER(raw_file[0:30])
            case 64:
                dib_header_decoding.dib_header_type = "OS22XBITMAPHEADER"
            case 16:
                dib_header_decoding.dib_header_type = "OS22XBITMAPHEADER_just_16b" #rest is \x00
            case 40:
                dib_header_decoding.dib_header_type = "BITMAPINFOHEADER"
                dib_header_decoding.get_info_from_BITMAPINFOHEADER(raw_file[0:60])
            case 52:
                dib_header_decoding.dib_header_type = "BITMAPV2INFOHEADER"
            case 56:
                dib_header_decoding.dib_header_type = "BITMAPV3INFOHEADER"
            case 108:
                dib_header_decoding.dib_header_type = "BITMAPV4HEADER"
            case 124:
                dib_header_decoding.dib_header_type = "BITMAPV5HEADER"
            # right now I'l only support BITMAPCOREHEADER(12) and BITMAPINFOHEADER(40)

        raw_image = raw_file[offset:len(raw_file)]

        #[] of rows: [] of pixels: [red, green, blue] #todo
        image = [[[0,0,0,0]]*dib_header_decoding.image_width]*int(math.fabs(dib_header_decoding.image_height))
        row_counter = len(image)-1
        column_counter = 0
        pixel_adress = 0

        bytes_per_pixel = dib_header_decoding.bits_per_pixel // 8

        if bytes_per_pixel == 3:
            while pixel_adress <= len(raw_image) - 3:
                image[row_counter][column_counter][0] = int.from_bytes([raw_image[pixel_adress + 0]], byteorder="little")
                image[row_counter][column_counter][1] = int.from_bytes([raw_image[pixel_adress + 1]], byteorder="little")
                image[row_counter][column_counter][2] = int.from_bytes([raw_image[pixel_adress + 2]], byteorder="little")

                pixel_adress += 3
                column_counter += 1

                if column_counter >= dib_header_decoding.image_width:
                    column_counter = 0
                    row_counter -= 1




        return(image)



#----------------------------------------------------------------------------------------------------------------------------------

class wav_file_processing:

    def num_to_bytes(num:int|list,length:int,signed = False)->bytes:
        # add big endian if needed
        #this is only little endian

        match length:
            case 1:
                format_string = "<c"
            case 2:
                if signed:
                    format_string = "h"
                else:
                    format_string = "H"
            case 4:
                if signed:
                    format_string = "i"
                else:
                    format_string = "I"
            case 8:
                if signed:
                    format_string = "q"
                else:
                    format_string = "Q"
            
        if type(num) == int:
            byte_num = pack(f"<{format_string}", num)
        else:
            byte_num = pack(f"<{len(num)}{format_string}", *num)
        

        return(byte_num)

    def make_wav(wave:list)->bytes:
        if len(wave)%2 != 0:
            wave.append(0)

        wave = sound_processing.normalize_wave(wave)



        file_type_bloc_id = b"RIFF"                                                                                 #4b
        file_size = wav_file_processing.num_to_bytes(len(wave) + 44 - 8,4) #- Overall file size -8                  #4b
        file_format_id = b"WAVE"                                                                                    #4b

        format_bloc_id = b"fmt\x20"                                                                                 #4b
        bloc_size = wav_file_processing.num_to_bytes(16,4)                                                          #4b
        audio_format = wav_file_processing.num_to_bytes(1,2)                                                        #2b
        number_of_channels = wav_file_processing.num_to_bytes(1,2)                                                  #2b
        sample_rate = wav_file_processing.num_to_bytes(config.sample_rate,4)                                      #4b
        byte_per_second = wav_file_processing.num_to_bytes(config.sample_rate * 1 * config.audio_resolution,4)  #4b
        byte_per_bloc = wav_file_processing.num_to_bytes(1 * config.audio_resolution,2)                           #2b
        bits_per_sample = wav_file_processing.num_to_bytes(config.audio_resolution * 8,2)                         #2b

        data_bloc_id = b"data"                                                                                      #4b
        data_size = wav_file_processing.num_to_bytes(len(wave)*config.audio_resolution,4)                         #4b
        data = wav_file_processing.num_to_bytes(wave,config.audio_resolution)

        #please don't judge me... at least it's readable...
        file_bytes = file_type_bloc_id + file_size + file_format_id
        file_bytes += format_bloc_id + bloc_size + audio_format + number_of_channels + sample_rate + byte_per_second + byte_per_bloc + bits_per_sample
        file_bytes += data_bloc_id + data_size + data

        return(file_bytes)


    def save_audio(name:str, file_bytes:bytes, extension:str):

        file = open(f"{name}{extension}", "wb+")
        file.write(file_bytes)
        file.close()
        print("ran successfully :D")
        return()


class sound_processing:
    def normalize_wave(wave_in:list)->list:
        wave_out = []
        wave_min = min(wave_in)
        wave_max = max(wave_in)
        for i in range(0,len(wave_in)):
            wave_out.append(math.floor((wave_in[i]-wave_min)/(wave_max-wave_min)*(math.pow(2,config.audio_resolution*8)-1)))
        return(wave_out)

    def make_sin(frequency:float,time:float,sample_num:int)->list:
            wave = []
            interval = time/sample_num
            for i in range(0,sample_num):
                wave.append(math.sin(2*math.pi*frequency*i*interval))
            return(wave)
    
    def x_noise_generator(length:int)->list:
        noise = []
        while len(noise) != length:
            noise.append(randint(0,255))

        return(noise)

    def modulate_wave(wave:list,amplitude:list)->list:
        for i in range(0,len(wave)):
            if i<len(amplitude):
                wave[i] = wave[i] * amplitude[i]
        return(wave)



#----------------------------------------------------------------------------------------------------------------------------------


#wav_file_processing.save_audio("x2",wav_file_processing.make_wav(sound_processing.make_sin(220,config.audio_length,config.sample_number)),".wav")
image_processing.get_image_data(config.image_target)
dib_header_decoding.print_header_info()






print(f"took {(perf_counter_ns() - start_time)/10**6} ms")


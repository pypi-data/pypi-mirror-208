import subprocess
import numpy
try:
    import matplotlib.pyplot as plt
except:
    print("install matplolib ...")
    subprocess.run('pip install matplolib',shell='true')
    import matplotlib.pyplot as plt
from matplotlib import colors
try:
    import xarray
except:
    print("install xarray ...")
    subprocess.run('pip install xarray',shell='true')
    import xarray
try:
    import sklearn
except:
    print("install sklean ...")
    subprocess.run('pip install -U scikit-learn',shell='true')
    import sklearn
    
try:
    from osgeo import gdal
except:
    #TODO set env conda env ไม่รู้จัก path
    raise ModuleNotFoundError('1.You have to install gdal first with this command "conda install -c conda-forge gdal" 2.pip install lazyearth again')
import os
# from keras import Sequential
# from keras.layers import Convolution2D

class objearth():
    def __init__(self):
        pass
    # def load_data(rgb):
    #     x = []
    #     x.append(rgb)
    #     return numpy.array(x)
    # def get_model(Xaxis,Yaxis):
    #     h5_dir = os.path.join(os.path.dirname(__file__), 'models')
    #     weights_path = os.path.join(h5_dir,'weights.h5')
    #     model = Sequential()
    #     model.add(
    #         Convolution2D(
    #             32, 9, activation="relu", input_shape=(Xaxis, Yaxis, 3), padding="same"
    #         )
    #     )
    #     model.add(Convolution2D(16, 5, activation="relu", padding="same"))
    #     model.add(Convolution2D(3, 5, activation="relu", padding="same"))
    #     if weights_path:
    #         model.load_weights(weights_path)
    #     model.compile(optimizer="adam", loss="mse", metrics=["accuracy"])
    #     return model
    # def superresolution(rgb):
    #     """
    #     superressolution of rgb image
    #     :param rgb : numpy rgb image 
    #     :return    : shapen image
    #     """
    #     # model_weights_path = r"C:\Users\tul\Desktop\models\weights.h5"
    #     Xa,Ya,_ = rgb.shape
    #     model = objearth.get_model(Xa,Ya)                #Prepare model
    #     x = objearth.load_data(rgb)
    #     out_array = model.predict(x)
    #     for index in range(out_array.shape[0]):
    #         num, rows, cols, channels = out_array.shape
    #         for i in range(rows):
    #             for j in range(cols):
    #                 for k in range(channels):
    #                     if out_array[index][i][j][k] > 1.0:
    #                         out_array[index][i][j][k] = 1.0
    #         # out_img = Image.fromarray(np.uint8(out_array[0] * 255))
    #         out_img = numpy.uint8(out_array[0] * 255)
    #     return out_img
    @staticmethod
    def montage(img1,img2):
        """
        compare 2 image.
        :param img1 : first array
        :param img2 : second array
        """
        plt.figure(figsize=(15,15))
        plt.subplot(121),plt.imshow(img1, cmap = 'gray')
        plt.title('Image 1'), plt.xticks([]), plt.yticks([])
        plt.subplot(122),plt.imshow(img2, cmap = 'viridis')
        plt.title('Image 2'), plt.xticks([]), plt.yticks([])
        plt.show()
        
    @staticmethod
    def falsecolor(Dataset1,Dataset2,Dataset3,bright=10):
        """
        combination 3 bands which any bands (Used with Xarray)
        :param Dataset1 : band 1
        :param Dataset1 : band 2
        :param Dataset3 : band 3
        :param bright   : brightness of image
        :return         : The stacked array 
        """
        BAND1    = xarray.where(Dataset1==-9999,numpy.nan,Dataset1)
        band1    = BAND1.to_numpy()/10000*bright
        BAND2    = xarray.where(Dataset2==-9999,numpy.nan,Dataset2)
        band2    = BAND2.to_numpy()/10000*bright
        BAND3    = xarray.where(Dataset3==-9999,numpy.nan,Dataset3)
        band3    = BAND3.to_numpy()/10000*bright
        product  = numpy.stack([band1,band2,band3],axis=2)
        return product

    @staticmethod
    def truecolor(Dataset,bright=10):
        """
        combination 3 bands which Red Green Blue bands (Used with Xarray)
        :param Dataset : Dataset of satellite bands
        :param bright  : brightness of image
        :return        : RGB array stacked 
        """
        RED    = xarray.where(Dataset.red==-9999,numpy.nan,Dataset.red)
        red    = RED.to_numpy()/10000*bright
        BLUE   = xarray.where(Dataset.blue==-9999,numpy.nan,Dataset.blue)
        blue   = BLUE.to_numpy()/10000*bright
        GREEN  = xarray.where(Dataset.green==-9999,numpy.nan,Dataset.green)
        green  = GREEN.to_numpy()/10000*bright
        rgb    = numpy.stack([red,green,blue],axis=2)
        return rgb

    @staticmethod
    def bandcombination(band1,band2,band3,bright=10):
        """
        combination 2 bands which Red,Green,Blue bands (Used with .tif file)
        :param band1 : band1
        :param band2 : band2
        :param band3 : band3
        :return      : numpy stacked array
        """
        b1  = band1/10000 *bright
        b2  = band2/10000 *bright
        b3  = band3/10000 *bright
        return numpy.stack([b1,b2,b3],axis=2)


    def clearcloud(self,Dataset0,Dataset1):
        '''
        Clear the clouds
        :param Dataset0 : The image that want to clear cloud.
        :param Dataset1 : The better image that used to maske the first image better.
        :return         : better cloud image
        '''
        self.Dataset0 = Dataset0
        self.Dataset1 = Dataset1
        pixel0 = self.Dataset0.pixel_qa
        mask1 = xarray.where(pixel0==352,1,0)    
        mask2 = xarray.where(pixel0==480,1,0)
        mask3 = xarray.where(pixel0==944,1,0)
        sum = mask1+mask2+mask3
        mask0 = xarray.where(sum.data>0,1,0)
        blue        = xarray.where(mask0,self.Dataset1.blue,self.Dataset0.blue)
        green       = xarray.where(mask0,self.Dataset1.green,self.Dataset0.green)
        red         = xarray.where(mask0,self.Dataset1.red,self.Dataset0.red)
        nir         = xarray.where(mask0,self.Dataset1.nir,self.Dataset0.nir)
        pixel_qa    = xarray.where(mask0,self.Dataset1.pixel_qa,self.Dataset0.pixel_qa)
        # Create DataArray
        return xarray.merge([blue,green,red,nir,pixel_qa])

    @staticmethod
    def plotshow(DataArray,cmap=True,area=True,ts=0.07,zenmode=False,figsize=(8,8),xlabel="x axis size",ylabel="y axis size",title=''):
        '''
        Plot image 
        :param DataArray : Numpy array/Xarray data array
        '''
        if type(DataArray) == xarray.core.dataarray.DataArray:
            if area==True:
                ymax = 0 ; ymin = DataArray.shape[0]
                xmin = 0 ; xmax = DataArray.shape[1] 
            else:
                ymax = area[0] ; ymin = area[1]
                xmin = area[2] ; xmax = area[3]
            lon  =  DataArray.longitude.to_numpy()[xmin:xmax]
            lon0 =  lon[0] ; lon1 =  lon[-1]
            lat  =  DataArray.latitude.to_numpy()[ymax:ymin]
            lat0 = -lat[-1] ; lat1 = -lat[0]
            def longitude(lon):
                return [lon0,lon1]
            def latitude(lat):
                return [lat0,lat1]
            def axis(x=0):
                return x
            fig,ax = plt.subplots(constrained_layout=True)
            fig.set_size_inches(figsize)
            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.imshow(DataArray[ymax:ymin,xmin:xmax],extent=[xmin,xmax,ymin,ymax])
            secax_x = ax.secondary_xaxis('top',functions=(longitude,axis))
            secax_x.set_xlabel('longitude')
            secax_x = ax.secondary_xaxis('top',functions=(longitude,axis))
            secax_x.set_xlabel('longitude')
            secax_y = ax.secondary_yaxis('right',functions=(latitude,axis))
            secax_y.set_ylabel('latitute')
            plt.grid(color='w', linestyle='-', linewidth=ts)
            plt.show()
        #Area
        elif type(DataArray) == numpy.ndarray:
            if area==True:
                ymax = 0 ; ymin = DataArray.shape[0]
                xmin = 0 ; xmax = DataArray.shape[1]
            else:
                ymax = area[0] ; ymin = area[1]
                xmin = area[2] ; xmax = area[3]
            real_margin_img = DataArray[ymax:ymin,xmin:xmax]

            #plotshow
            plt.figure(figsize=(figsize))
            plt.subplots(constrained_layout=True)
            color_map = plt.imshow(real_margin_img,extent=[xmin,xmax,ymin,ymax])
            if zenmode != True:
                plt.title(title)
                plt.xlabel(xlabel)
                plt.ylabel(ylabel)
                plt.grid(color='w', linestyle='-', linewidth=ts)
            else:
                plt.axis('off')

            # faction
            im_ratio = real_margin_img.shape[1]/real_margin_img.shape[0]
            if im_ratio<1:
                fac = 0.0485
            elif im_ratio==1:
                fac = 0.045
            else:
                fac = 0.0456*(im_ratio**(-1.0113))
            #print(real_margin_img.shape[1],real_margin_img.shape[0],im_ratio,fac)

            #colorbar
            min = real_margin_img.min()
            max = real_margin_img.max()
            plt.clim(min,max)
            if cmap==True:
                color_map.set_cmap('viridis')
            else:
                color_map.set_cmap(cmap)
            plt.colorbar(orientation="vertical",fraction=fac)
            plt.show()

        else:
            print("Nonetype :",type(DataArray))
            

    def percentcloud(self,Dataset):
        '''
        :param Dataset : Xarray dataset pixel_qa bands
        :return        : percent of the cloud in the image
        '''
        self.Dataset = Dataset
        FashCloud = [352,480,944]
        dstest    = self.Dataset.pixel_qa
        dsnew     = xarray.where(dstest == FashCloud[0],numpy.nan,dstest)
        dsnew     = xarray.where(dsnew  == FashCloud[1],numpy.nan,dsnew)
        dsnew     = xarray.where(dsnew  == FashCloud[2],numpy.nan,dsnew)
        Cpixel    = (numpy.isnan(dsnew.to_numpy())).sum()
        Allpixel  = int(self.Dataset.pixel_qa.count())
        Cloudpercent = (Cpixel/Allpixel)*100
        print("Percent Cloud : %.4f"%Cloudpercent,"%")


################################################### INDEX ###################################################
    @staticmethod
    def NDVI(DataArray):
        """
        calc NDVI (Normalized Difference vegetation Index)
        :param DataArray : (Red bands,NIR bands):
        :return          : NDVI array
        """
        DataArray = DataArray
        red = xarray.where(DataArray.red==-9999,numpy.nan,DataArray.red)
        nir = xarray.where(DataArray.nir==-9999,numpy.nan,DataArray.nir)
        ndvi1 = (nir-red)/(nir+red).to_numpy()
        ndvi3 = numpy.clip(ndvi1,-1,1)
        return ndvi3
    @staticmethod
    def EVI(DataArray):
        """
        calc EVI (Enhanced Vegetation Index)
        :param DataArray : (RED bands,BLUE bands,NIR bands):
        :return          : EVI array
        """
        red  = xarray.where(DataArray.red==-9999,numpy.nan,DataArray.red)
        blue = xarray.where(DataArray.blue==-9999,numpy.nan,DataArray.blue)
        nir  = xarray.where(DataArray.nir==-9999,numpy.nan,DataArray.nir)
        evi1 = (nir-red)/(nir+6*red-7.5*blue+1).to_numpy()
        evi3 = numpy.clip(evi1,-1,1)
        return evi3
    @staticmethod
    def NDMI(DataArray):
        """
        calc NDMI (Normalized Difference Moisture Index)
        :param DataArray : (SWIR-1 bands,NIR bands):
        :return          : NDMI array
        """
        if 'swir_1' in DataArray.data_vars:
            swir1 = DataArray.swir_1
        swir1 = DataArray.swir1
        swir  = xarray.where(swir1==-9999,numpy.nan,swir1)
        nir   = xarray.where(DataArray.nir==-9999,numpy.nan,DataArray.nir)
        ndmi1 = (nir-swir)/(nir+swir).to_numpy()
        ndmi3 = numpy.clip(ndmi1,-1,1)
        return ndmi3
    @staticmethod
    def BSI(DataArray):
        """
        calc BSI (Bare Soil Index)
        :param DataArray : (GREEN bands,NIR bands):
        :return          : BSI array
        """
        if 'swir_1' in DataArray.data_vars:
            swir1 = DataArray.swir_1
        swir1 = DataArray.swir1
        swir  = xarray.where(swir1==-9999,numpy.nan,swir1)
        red   = xarray.where(DataArray.red==-9999,numpy.nan,DataArray.red)
        blue   = xarray.where(DataArray.blue==-9999,numpy.nan,DataArray.blue)
        nir   = xarray.where(DataArray.nir==-9999,numpy.nan,DataArray.nir)
        bsi1 = ((red+swir) - (nir+blue)) / ((red+swir) + (nir+blue)).to_numpy()
        bsi3 = numpy.clip(bsi1,-1,1)
        return bsi3
    @staticmethod
    def NDWI(DataArray):
        """
        calc NDWI (Normalized Difference Water Index)
        :param DataArray : (SWIR bands,NIR bands):
        :return          : NDMI array
        """
        if 'swir_1' in DataArray.data_vars:
            swir1 = DataArray.swir_1
        swir1 = DataArray.swir1
        swir  = xarray.where(swir1==-9999,numpy.nan,swir1)
        nir   = xarray.where(DataArray.nir==-9999,numpy.nan,DataArray.nir)
        ndwi1 = (nir-swir)/(nir+swir).to_numpy()
        ndwi3 = numpy.clip(ndwi1,-1,1)
        return ndwi3
    @staticmethod
    def NMDI(DataArray):
        """
        calc NMDI (Normalized Multi-Band Drought Index)
        :param DataArray : (SWIR1 bands,SWIR2 bands,NIR bands):
        :return          : NMDI array
        """
        if 'swir_1' in DataArray.data_vars:
            swir1 = DataArray.swir_1
        swir1 = DataArray.swir1
        if 'swir_2' in DataArray.data_vars:
            swir2 = DataArray.swir_2
        swir2 = DataArray.swir1
        swir1 = xarray.where(swir1==-9999,numpy.nan,swir1)
        swir2 = xarray.where(swir2==-9999,numpy.nan,swir2)
        nir   = xarray.where(DataArray.nir==-9999,numpy.nan,DataArray.nir)
        nmdi1 = (nir-(swir1-swir2))/(nir-(swir1+swir2)).to_numpy()
        nmdi3 = numpy.clip(nmdi1,-1,1)
        return nmdi3
    @staticmethod
    def NDDI(DataArray):
        """
        calc NDDI (Normalized Difference Drought Index)
        :param DataArray : (RED bands,NIR bands,SWIR bands):
        :return          : NDDI array
        """
        if 'swir_1' in DataArray.data_vars:
            swir1 = DataArray.swir_1
        swir1 = DataArray.swir1
        red = xarray.where(DataArray.red==-9999,numpy.nan,DataArray.red)
        nir = xarray.where(DataArray.nir==-9999,numpy.nan,DataArray.nir)
        swir = xarray.where(swir1==-9999,numpy.nan,swir1)
        ndvi = (nir-red)/(nir+red)
        ndwi = (nir-swir)/(nir+swir)       
        nddi1 = (ndvi-ndwi)/(ndvi+ndwi).to_numpy() 
        nddi3 = numpy.clip(nddi1,-1,1)
        return nddi3
#############################################################################################################
    # # @staticmethod
    # def NDGI(DataArray):
    #     """
    #     Normalized Difference Glacier Index (NDGI) ???
    #     :param DataArray : (SWIR bands,NIR bands):
    #     :return          : NDMI array
    #     """
    #     blue   = xarray.where(DataArray.blue==-9999,numpy.nan,DataArray.blue)     #band2
    #     green  = xarray.where(DataArray.green==-9999,numpy.nan,DataArray.green)   #band3
    #     red    = xarray.where(DataArray.red==-9999,numpy.nan,DataArray.red)       #band4
    #     nir   = xarray.where(DataArray.nir==-9999,numpy.nan,DataArray.nir)        #band5
    #     if 'swir_1' in DataArray.data_vars:
    #         swir1 = DataArray.swir_1
    #     swir1 = DataArray.swir1                                                   #band6
    #     if 'swir_2' in DataArray.data_vars:
    #         swir2 = DataArray.swir_2
    #     swir2 = DataArray.swir2                                                   #band7
    #     fml = (green-swir1)/(green+swir1)
    #     val = fml.to_numpy()
    #     val = numpy.clip(val,-1,1)
    #     return val
    @staticmethod
    def NDWI(DataArray):
        """
        calc NDWI (Normalized Difference Water Index)
        :param DataArray : (SWIR bands,NIR bands):
        :return          : NDMI array
        """
        if 'swir_1' in DataArray.data_vars:
            swir1 = DataArray.swir_1
        swir1 = DataArray.swir1
        swir  = xarray.where(swir1==-9999,numpy.nan,swir1)
        nir   = xarray.where(DataArray.nir==-9999,numpy.nan,DataArray.nir)
        ndwi1 = (nir-swir)/(nir+swir).to_numpy()
        ndwi3 = numpy.clip(ndwi1,-1,1)
        return ndwi3
    @staticmethod
    def AVI(DataArray):
        """
        calc Advanced Vegetation Index (AVI)
        :param DataArray : (SWIR bands,NIR bands):
        :return          : NDMI array
        """
        red   = xarray.where(DataArray.red==-9999,numpy.nan,DataArray.red)
        nir   = xarray.where(DataArray.nir==-9999,numpy.nan,DataArray.nir)

        val = (nir*(1-red)*(nir-red))**1/3
        val = val.to_numpy()
        output = numpy.clip(val,-1,1)
        return output
    @staticmethod
    def SI(DataArray):
        """
        calc Shadow Index (SI) ???
        :param DataArray : (SWIR bands,NIR bands):
        :return          : NDMI array
        """
        blue   = xarray.where(DataArray.blue==-9999,numpy.nan,DataArray.blue)
        green  = xarray.where(DataArray.green==-9999,numpy.nan,DataArray.green)
        red    = xarray.where(DataArray.red==-9999,numpy.nan,DataArray.red)
        fml = ((1-blue)*(1-green)*(1-red))**(1/3)
        val = fml.to_numpy()
        val = numpy.clip(val,-1,1)
        return val
    @staticmethod
    def NDSI(DataArray):
        """
        Normalized Difference Snow Index (NDSI)
        :param DataArray : (SWIR bands,NIR bands):
        :return          : NDMI array
        """
        green  = xarray.where(DataArray.green==-9999,numpy.nan,DataArray.green)   #band3
        if 'swir_1' in DataArray.data_vars:
            swir1 = DataArray.swir_1
        swir1 = DataArray.swir1                                                   #band6
        fml = (green-swir1)/(green+swir1)
        val = fml.to_numpy()
        val = numpy.clip(val,-1,1)
        return val
    @staticmethod
    def NDGI(DataArray):
        """
        Normalized Difference Glacier Index (NDGI)
        :param DataArray : (SWIR bands,NIR bands):
        :return          : NDMI array
        """
        green  = xarray.where(DataArray.green==-9999,numpy.nan,DataArray.green)   #band3
        red    = xarray.where(DataArray.red==-9999,numpy.nan,DataArray.red)       #band4
        fml = (green-red)/(green+red)
        val = fml.to_numpy()
        val = numpy.clip(val,-1,1)
        return val
    @staticmethod
    def NBRI(DataArray):
        """
        Normalized Burned Ratio Index (NBRI)
        :param DataArray : (SWIR bands,NIR bands):
        :return          : NDMI array
        """
        nir   = xarray.where(DataArray.nir==-9999,numpy.nan,DataArray.nir)        #band5
        if 'swir_2' in DataArray.data_vars:
            swir2 = DataArray.swir_2
        swir2 = DataArray.swir2                                                   #band7
        fml = (nir-swir2)/(nir+swir2)
        val = fml.to_numpy()
        val = numpy.clip(val,-1,1)
        return val
    @staticmethod
    def NDGI(DataArray):
        """
        Normalized Pigment Chlorophyll Ratio Index (NPCRI)
        :param DataArray : (SWIR bands,NIR bands):
        :return          : NDMI array
        """
        blue   = xarray.where(DataArray.blue==-9999,numpy.nan,DataArray.blue)     #band2
        red    = xarray.where(DataArray.red==-9999,numpy.nan,DataArray.red)       #band4
        fml = (red-blue)/(red+blue)
        val = fml.to_numpy()
        val = numpy.clip(val,-1,1)
        return val
#############################################################################################################

    def genimg(size=[2,2],range=[-1,1],nan=0,inf=0):
        """
        Generate 1D images with random values.
        :param size  : size of image
        :param range : Range of value
        :param nan   : Number of NaN
        :param inf   : Number of Inf
        :return      : 1D array image
        """
        data = numpy.random.uniform(range[0],range[1],[size[0],size[1]])
        index_nan = numpy.random.choice(data.size,nan,replace=1)
        data.ravel()[index_nan] = numpy.nan
        index_inf = numpy.random.choice(data.size,inf,replace=1)
        data.ravel()[index_inf] = numpy.inf
        return data

    @staticmethod
    def bandopen(target):
        """
        Open TIFF image
        :param target : path of image
        :return       : ndarray
        """
        return gdal.Open(target).ReadAsArray()

    # @staticmethod
    # def geo_save(array,filename,geo_transform = (0.0,1.0,0.0,0.0,0.0,1.0),projection='',dtype=gdal.GDT_Byte):
    #     """
    #     Save array to image
    #     :param array    : ndarray
    #     :param filename : filename
    #     :return         : TIFF image 
    #     """
    #     filename = Path(os.getcwd()).joinpath(filename+'.tif').as_posix()
    #     cols = array.shape[1]
    #     rows = array.shape[0]
    #     driver = gdal.GetDriverByName('GTiff')
    #     out_raster = driver.Create(filename,cols,rows,1,dtype,options=['COMPRESS=PACKBITS'])
    #     out_raster.SetGeoTransform(geo_transform)
    #     out_raster.SetProjection(projection)
    #     outband=out_raster.GetRasterBand(1)
    #     outband.SetNoDataValue(0)
    #     outband.WriteArray(array)
    #     outband.FlushCache()
    #     print('Saving image: '+filename)
    
    @staticmethod
    def gengaussian(x_size,y_size):
        """
        Create gaussian function array
        :param x_size : number
        :param y_size : number
        :return: gaussian ndarray
        """
        x, y = numpy.meshgrid(numpy.linspace(-1,1,x_size), numpy.linspace(-1,1,y_size))
        d = numpy.sqrt(x*x+y*y)
        sigma, mu = 0.5, 1.0
        g = numpy.exp(-( (d-mu)**2 / ( 2.0 * sigma**2 ) ) )
        return g

    # def _inter_from_256(x):
    #     return np.interp(x=x,xp=[0,255],fp=[0,1])
    # def __rgb_to_colormapcode(r,g,b):
    #     return (_inter_from_256(r),_inter_from_256(g),_inter_from_256(b))
    
    @staticmethod
    def bluesea():
        """
        Bluesea colormap used for waterqualtiy.
        :return : colormap.
        """
        RGB6 = (0.1       , 0.1       , 0.1       )     #RGB(252,252,252)
        RGB5 = (0.        , 0.31372549, 0.45098039)     #RGB(114,199,236)
        RGB4 = (0.0627451 , 0.49019608, 0.6745098 )     #RGB(30,186,214)
        RGB3 = (0.09411765, 0.60392157, 0.82745098)     #RGB(23,153,210)
        RGB2 = (0.11764706, 0.73333333, 0.84313725)     #RGB(16,125,171)
        RGB1 = (0.44313725, 0.78039216, 0.9254902 )     #RGB(0,79,113)
        # RGB0 = (0.99      , 0.99      , 0.99      )     #RGB(25,25,25)
        RGB0 = (1.00      , 1.00      , 1.00      )     #RGB(0,0,0)
        cdict = {
            'red':  ((1  / 6 * 0, RGB0[0]  ,RGB0[0]),
                    (1  / 6 * 1, RGB1[0]  ,RGB1[0]),
                    (1  / 6 * 2, RGB2[0]  ,RGB2[0]),
                    (1  / 6 * 3, RGB3[0]  ,RGB3[0]),
                    (1  / 6 * 4, RGB4[0]  ,RGB4[0]),
                    (1  / 6 * 5, RGB5[0]  ,RGB5[0]),
                    (1  / 6 * 6, RGB6[0]  ,RGB6[0])
                    ),
            'green':((1  / 6 * 0, RGB0[1]    , RGB0[1]),
                    (1  / 6 * 1, RGB1[1]    , RGB1[1]),
                    (1  / 6 * 2, RGB2[1]    , RGB2[1]),
                    (1  / 6 * 3, RGB3[1]    , RGB3[1]),
                    (1  / 6 * 4, RGB4[1]    , RGB4[1]),
                    (1  / 6 * 5, RGB5[1]    , RGB5[1]),
                    (1  / 6 * 6, RGB6[1]    , RGB6[1])
                    ),
            'blue': ((1  / 6 * 0, RGB0[2]    , RGB0[2]),
                    (1  / 6 * 1, RGB1[2]    , RGB1[2]),
                    (1  / 6 * 2, RGB2[2]    , RGB2[2]),
                    (1  / 6 * 3, RGB3[2]    , RGB3[2]),
                    (1  / 6 * 4, RGB4[2]    , RGB4[2]),
                    (1  / 6 * 5, RGB5[2]    , RGB5[2]),
                    (1  / 6 * 6, RGB6[2]    , RGB6[2])
                    ),
        }
        nc = colors.LinearSegmentedColormap('bluesea',segmentdata=cdict)
        return nc    
    
    @staticmethod
    def leafwood():
        """
        Leafwood colormap used for NDVI.
        :return : colormap.
        """
        #https://mycolor.space/gradient?ori=to+right+top&hex=%2385A938&hex2=%233C770E&sub=1
        #https://imagecolorpicker.com/en
        RGB1   = (0.30588235, 0.05490196, 0.05490196)   #RGB(78,14,14)          
        RGB2   = (0.39215686, 0.09803922, 0.07843137)   #RGB(100,25,20)
        RGB3   = (0.43921569, 0.18431373, 0.00392157)   #RGB(112,47,1)
        RGB4   = (0.50980392, 0.23529412, 0.05098039)   #RGB(130,60,13)
        RGB5   = (0.54901961, 0.2745098 , 0.05882353)   #RGB(140,70,15)
        RGB6   = (0.61960784, 0.30588235, 0.02745098)   #RGB(158,78,7)
        RGB7   = (0.70980392, 0.40784314, 0.0627451 )   #RGB(181,104,16) 
        RGB8   = (0.79607843, 0.49019608, 0.16470588)   #RGB(203, 125, 42)
        RGB9   = (0.85490196, 0.58823529, 0.04705882)   #RGB(218,150,12)
        RGB10  = (0.85882353, 0.63529412, 0.05490196)   #RGB(219,162,14)
        RGB11  = (0.88235294, 0.7254902 , 0.01568627)   #RGB(225,185,4)
        RGB12  = (0.87058824, 0.8       , 0.05098039)   #RGB(222,204,13)
        RGB13  = (0.89019608, 0.8745098 , 0.07058824)   #RGB(227,223,18)
        RGB14  = (0.92156863, 0.91764706, 0.09019608)   #RGB(235,234,23)
        RGB15  = (0.81176471, 0.85882353, 0.2745098 )   #RGB(207,219,70)
        RGB16  = (0.68627451, 0.77647059, 0.26666667)   #RGB(175,198,68)
        RGB17  = (0.56078431, 0.69803922, 0.25882353)   #RGB(143,178,66)
        RGB18  = (0.52156863, 0.6627451 , 0.21960784)   #RGB(133,169,56)
        RGB19  = (0.38039216, 0.56470588, 0.14117647)   #RGB(97, 144, 36)
        RGB20  = (0.23529412, 0.46666667, 0.05490196)   #RGB(60,119,14)
        RGB21  = (0.16078431, 0.36862745, 0.04313725)   #RGB(41,94,11)
        cdict = {
            'red':  ((1  / 20 * 0,  (RGB1[0])  ,(RGB1[0])),
                    (1  / 20 * 1,  (RGB2[0])  ,(RGB2[0])),
                    (1  / 20 * 2,  (RGB3[0])  ,(RGB3[0])),
                    (1  / 20 * 3,  (RGB4[0])  ,(RGB4[0])),
                    (1  / 20 * 4,  (RGB5[0])  ,(RGB5[0])),
                    (1  / 20 * 5,  (RGB6[0])  ,(RGB6[0])),
                    (1  / 20 * 6,  (RGB7[0])  ,(RGB7[0])),
                    (1  / 20 * 7,  (RGB8[0])  ,(RGB8[0])),
                    (1  / 20 * 8,  (RGB9[0])  ,(RGB9[0])),
                    (1  / 20 * 9,  (RGB10[0])  ,(RGB10[0])),
                    (1  / 20 * 10, (RGB11[0])  ,(RGB11[0])),
                    (1  / 20 * 11, (RGB12[0])  ,(RGB12[0])),
                    (1  / 20 * 12, (RGB13[0])  ,(RGB13[0])),
                    (1  / 20 * 13, (RGB14[0])  ,(RGB14[0])),
                    (1  / 20 * 14, (RGB15[0])  ,(RGB15[0])),
                    (1  / 20 * 15, (RGB16[0])  ,(RGB16[0])),
                    (1  / 20 * 16, (RGB17[0])  ,(RGB17[0])),
                    (1  / 20 * 17, (RGB18[0])  ,(RGB18[0])),
                    (1  / 20 * 18, (RGB19[0])  ,(RGB19[0])),
                    (1  / 20 * 19, (RGB20[0])  ,(RGB20[0])),
                    (1  / 20 * 20, (RGB21[0])  ,(RGB21[0]))),
            'green':((1  / 20 * 0,  (RGB1[1])  ,(RGB1[1])),
                    (1  / 20 * 1,  (RGB2[1])  ,(RGB2[1])),
                    (1  / 20 * 2,  (RGB3[1])  ,(RGB3[1])),
                    (1  / 20 * 3,  (RGB4[1])  ,(RGB4[1])),
                    (1  / 20 * 4,  (RGB5[1])  ,(RGB5[1])),
                    (1  / 20 * 5,  (RGB6[1])  ,(RGB6[1])),
                    (1  / 20 * 6,  (RGB7[1])  ,(RGB7[1])),
                    (1  / 20 * 7,  (RGB8[1])  ,(RGB8[1])),
                    (1  / 20 * 8,  (RGB9[1])  ,(RGB9[1])),
                    (1  / 20 * 9,  (RGB10[1])  ,(RGB10[1])),
                    (1  / 20 * 10, (RGB11[1])  ,(RGB11[1])),
                    (1  / 20 * 11, (RGB12[1])  ,(RGB12[1])),
                    (1  / 20 * 12, (RGB13[1])  ,(RGB13[1])),
                    (1  / 20 * 13, (RGB14[1])  ,(RGB14[1])),
                    (1  / 20 * 14, (RGB15[1])  ,(RGB15[1])),
                    (1  / 20 * 15, (RGB16[1])  ,(RGB16[1])),
                    (1  / 20 * 16, (RGB17[1])  ,(RGB17[1])),
                    (1  / 20 * 17, (RGB18[1])  ,(RGB18[1])),
                    (1  / 20 * 18, (RGB19[1])  ,(RGB19[1])),
                    (1  / 20 * 19, (RGB20[1])  ,(RGB20[1])),
                    (1  / 20 * 20, (RGB21[1])  ,(RGB21[1]))),
            'blue': ((1  / 20 * 0,  (RGB1[2])  ,(RGB1[2])),
                    (1  / 20 * 1,  (RGB2[2])  ,(RGB2[2])),
                    (1  / 20 * 2,  (RGB3[2])  ,(RGB3[2])),
                    (1  / 20 * 3,  (RGB4[2])  ,(RGB4[2])),
                    (1  / 20 * 4,  (RGB5[2])  ,(RGB5[2])),
                    (1  / 20 * 5,  (RGB6[2])  ,(RGB6[2])),
                    (1  / 20 * 6,  (RGB7[2])  ,(RGB7[2])),
                    (1  / 20 * 7,  (RGB8[2])  ,(RGB8[2])),
                    (1  / 20 * 8,  (RGB9[2])  ,(RGB9[2])),
                    (1  / 20 * 9,  (RGB10[2])  ,(RGB10[2])),
                    (1  / 20 * 10, (RGB11[2])  ,(RGB11[2])),
                    (1  / 20 * 11, (RGB12[2])  ,(RGB12[2])),
                    (1  / 20 * 12, (RGB13[2])  ,(RGB13[2])),
                    (1  / 20 * 13, (RGB14[2])  ,(RGB14[2])),
                    (1  / 20 * 14, (RGB15[2])  ,(RGB15[2])),
                    (1  / 20 * 15, (RGB16[2])  ,(RGB16[2])),
                    (1  / 20 * 16, (RGB17[2])  ,(RGB17[2])),
                    (1  / 20 * 17, (RGB18[2])  ,(RGB18[2])),
                    (1  / 20 * 18, (RGB19[2])  ,(RGB19[2])),
                    (1  / 20 * 19, (RGB20[2])  ,(RGB20[2])),
                    (1  / 20 * 20, (RGB21[2])  ,(RGB21[2])),
            )
        }
        nc4 = colors.LinearSegmentedColormap('leafwood',segmentdata=cdict)
        return nc4

    @staticmethod
    def sweetrose():
        """
        Sweetrose colormap used for NDVI.
        :return : colormap.
        """
        RGB1  = (1.        , 1.        , 1.        )    # rgba(254,254,254,255)
        RGB2  = (0.98823529, 0.88627451, 0.98823529)    # rgba(254,225,253,255)
        RGB3  = (0.98823529, 0.79215686, 0.99607843)    # rgba(252,202,254,255)
        RGB4  = (0.98823529, 0.79215686, 0.99607843)    # rgba(248,129,255,255)
        RGB5  = (0.96470588, 0.02352941, 1.        )    # rgba(235,14,243,255)
        RGB6  = (0.96470588, 0.01960784, 0.40784314)    # rgba(244,6,102,255)
        RGB8  = (0.96078431, 0.01960784, 0.        )    # rgba(251,2,0,255)
        RGB7  = (0.98431373, 0.35294118, 0.03529412)    # rgba(244,90,0,255)
        RGB9  = (0.98039216, 0.6745098 , 0.00392157)    # rgba(250,169,6,255)
        RGB10 = (0.96862745, 0.8       , 0.01176471)    # rgba(242,204,16,255)
        RGB11 = (0.99607843, 0.99215686, 0.01568627)    # rgba(255,253,8,255)
        RGB12 = (0.02745098, 0.58431373, 0.18039216)    # rgba(3,150,51,255)
        RGB13 = (0.02352941, 0.6627451 , 0.03137255)    # rgba(7,170,2,255)
        RGB14 = (0.04705882, 0.98039216, 0.02352941)    # rgba(12,250,4,255)
        RGB15 = (0.03921569, 0.97647059, 0.50980392)    # rgba(8,250,130,255)

        cdict = {
            'red':  ((1  / 14 * 0,  (RGB1[0])  ,(RGB1[0])),
                    (1  / 14 * 1,  (RGB2[0])  ,(RGB2[0])),
                    (1  / 14 * 2,  (RGB3[0])  ,(RGB3[0])),
                    (1  / 14 * 3,  (RGB4[0])  ,(RGB4[0])),
                    (1  / 14 * 4,  (RGB5[0])  ,(RGB5[0])),
                    (1  / 14 * 5,  (RGB6[0])  ,(RGB6[0])),
                    (1  / 14 * 6,  (RGB7[0])  ,(RGB7[0])),
                    (1  / 14 * 7,  (RGB8[0])  ,(RGB8[0])),
                    (1  / 14 * 8,  (RGB9[0])  ,(RGB9[0])),
                    (1  / 14 * 9,  (RGB10[0])  ,(RGB10[0])),
                    (1  / 14 * 10, (RGB11[0])  ,(RGB11[0])),
                    (1  / 14 * 11, (RGB12[0])  ,(RGB12[0])),
                    (1  / 14 * 12, (RGB13[0])  ,(RGB13[0])),
                    (1  / 14 * 13, (RGB14[0])  ,(RGB14[0])),
                    (1  / 14 * 14, (RGB15[0])  ,(RGB15[0]))),
            'green':((1  / 14 * 0,  (RGB1[1])  ,(RGB1[1])),
                    (1  / 14 * 1,  (RGB2[1])  ,(RGB2[1])),
                    (1  / 14 * 2,  (RGB3[1])  ,(RGB3[1])),
                    (1  / 14 * 3,  (RGB4[1])  ,(RGB4[1])),
                    (1  / 14 * 4,  (RGB5[1])  ,(RGB5[1])),
                    (1  / 14 * 5,  (RGB6[1])  ,(RGB6[1])),
                    (1  / 14 * 6,  (RGB7[1])  ,(RGB7[1])),
                    (1  / 14 * 7,  (RGB8[1])  ,(RGB8[1])),
                    (1  / 14 * 8,  (RGB9[1])  ,(RGB9[1])),
                    (1  / 14 * 9,  (RGB10[1])  ,(RGB10[1])),
                    (1  / 14 * 10, (RGB11[1])  ,(RGB11[1])),
                    (1  / 14 * 11, (RGB12[1])  ,(RGB12[1])),
                    (1  / 14 * 12, (RGB13[1])  ,(RGB13[1])),
                    (1  / 14 * 13, (RGB14[1])  ,(RGB14[1])),
                    (1  / 14 * 14, (RGB15[1])  ,(RGB15[1]))),
            'blue': ((1  / 14 * 0,  (RGB1[2])  ,(RGB1[2])),
                    (1  / 14 * 1,  (RGB2[2])  ,(RGB2[2])),
                    (1  / 14 * 2,  (RGB3[2])  ,(RGB3[2])),
                    (1  / 14 * 3,  (RGB4[2])  ,(RGB4[2])),
                    (1  / 14 * 4,  (RGB5[2])  ,(RGB5[2])),
                    (1  / 14 * 5,  (RGB6[2])  ,(RGB6[2])),
                    (1  / 14 * 6,  (RGB7[2])  ,(RGB7[2])),
                    (1  / 14 * 7,  (RGB8[2])  ,(RGB8[2])),
                    (1  / 14 * 8,  (RGB9[2])  ,(RGB9[2])),
                    (1  / 14 * 9,  (RGB10[2])  ,(RGB10[2])),
                    (1  / 14 * 10, (RGB11[2])  ,(RGB11[2])),
                    (1  / 14 * 11, (RGB12[2])  ,(RGB12[2])),
                    (1  / 14 * 12, (RGB13[2])  ,(RGB13[2])),
                    (1  / 14 * 13, (RGB14[2])  ,(RGB14[2])),
                    (1  / 14 * 14, (RGB15[2])  ,(RGB15[2])),
            )
        }
        nc5 = colors.LinearSegmentedColormap('new_cmap',segmentdata=cdict)
        return nc5

    # def stamp(param=''):
    #     import datetime,platform
    #     print(datetime.datetime.now().strftime('"""\n%c'))
    #     print('name:',param)
    #     print('OS system: ',platform.system())
    #     print('@author: Tun.k\n"""')
    # # stamp()



from sklearn.preprocessing import MinMaxScaler, RobustScaler
from sklearn.model_selection import train_test_split
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import calinski_harabasz_score
from sklearn.naive_bayes import GaussianNB
from sklearn import cluster
import numpy as np
from matplotlib import colorbar


class water:
        #fix
        required_bands = {'mndi','Green','ndwi','Mir2','mbwi'}
        required_indices = {'ndwi','mbwi','mndwi'}
        bands_keys = ['mndwi','ndwi','Mir2']
        invalid_mask = None
        glint_processor = None
        # config = config
        data_as_columns = None
        clusters_labels = None
        clusters_params = None
        cluster_matrix = None
        water_cluster = None
        water_mask = None
        best_k = None
        _product_name = None
        # bands_keys = bands_keys
        cluster_matrix = None
        train_size = 0.2
        min_train_size = 500
        max_train_size = 10000
        linkage = 'average'
        clip_band = ['mndwi', 'Mir2', 'ndwi']
        clip_inf_value = [-0.1, None, -0.15]
        clip_sup_value = [None, 0.075, None]
        glint_mode = True
        glint_processor = None
        detect_water_cluster = 'maxmndwi'
        min_k = 2
        score_index = 'calinsk'
        #unfix
        max_k = 5
        classifier = 'naivebayes'
        clustering_method = 'agglomerative'
        
        def __init__(self,dataset):
            # new
            if isinstance(dataset,xarray.core.dataset.Dataset):
                try:
                    red   = dataset.red.to_numpy()
                    green = dataset.green.to_numpy()
                    blue  = dataset.blue.to_numpy()
                    nir   = dataset.nir.to_numpy()
                    if 'swir1' in dataset.data_vars:
                        mir = dataset.swir1
                    elif 'swir_1' in dataset.data_vars:
                        mir = dataset.swir_1
                    else:
                        raise ValueError("Error to load swir1 band")
                    mir   = mir.to_numpy()
                    if 'swir2' in dataset.data_vars:
                        mir2 = dataset.swir1
                    elif 'swir_2' in dataset.data_vars:
                        mir2 = dataset.swir_1
                    else:
                        raise ValueError("Error to load swir2 band")
                    mir2   = mir2.to_numpy()
                except ValueError as e:
                    print(e)
                bands = {'Red':red,
                        'Green':green,
                        'Blue':blue,
                        'Nir':nir,
                        'Mir':mir,
                        'Mir2':mir2}
                dataset = bands
            # old
            self.input_bands = dataset
            bands = dict()
            for i,j in self.input_bands.items():
                quantize = j.squeeze()/10000
                bands.update({i:quantize})
            self.bands=bands

        def __str__(self):
            lst = list()
            for i in self.bands.keys():
                lst.append(i)
            lst = str(lst)
            return "bands : "+lst 
    
        def show(self):
            # oe.plotshow(oe.band_combination(self.bands['Red'],self.bands['Green'],self.bands['Blue'],5))
            print(self.bands)
            
        ############################################ DWImageClustering ############################################
        #check if the MNDWI index is necessary and if it exists
        @staticmethod
        def calc_normalized_difference(img1, img2, mask=None, compress_cte=0.02):
            """
            Calc the normalized difference of given arrays (img1 - img2)/(img1 + img2).
            Updates the mask if any invalid numbers (ex. np.inf or np.nan) are encountered
            :param img1         : first array
            :param img2         : second array
            :param mask         : initial mask, that will be updated
            :param compress_cte : amount of index compression. The greater, the more the index will be compressed towards 0
            :return             : nd array filled with -9999 in the mask and the mask itself
            """
            # create a minimum array
            min_values = np.where(img1 < img2, img1, img2)
            # then create the to_add matrix (min values turned into positive + epsilon)
            min_values = np.where(min_values <= 0, -min_values + 0.001, 0) + compress_cte
            nd = ((img1 + min_values) - (img2 + min_values)) / ((img1 + min_values) + (img2 + min_values))
            # Clipping value
            nd[nd > 1] = 1
            nd[nd < -1] = -1
            # https://github.com/olivierhagolle/modified_NDVI
            # if result is infinite, result should be 1
            nd[np.isinf(nd)] = 1
            # nd_mask = np.isinf(nd) | np.isnan(nd) | mask
            nd_mask = np.isnan(nd) | (mask if mask is not None else False)
            nd = np.ma.array(nd, mask=nd_mask, fill_value=-9999)
            return nd.filled(), nd.mask

        @staticmethod
        #check if the MBWI index exist
        def calc_mbwi(bands, factor, mask):
            # changement for negative SRE values scene
            min_cte = np.min([np.min(bands['Green'][~mask]), np.min(bands['Red'][~mask]),
                                np.min(bands['Nir'][~mask]), np.min(bands['Mir'][~mask]), np.min(bands['Mir2'][~mask])])
            if min_cte <= 0:
                min_cte = -min_cte + 0.001
            else:
                min_cte = 0
            mbwi = factor * (bands['Green'] + min_cte) - (bands['Red'] + min_cte) - (bands['Nir'] + min_cte) \
                    - (bands['Mir'] + min_cte) - (bands['Mir2'] + min_cte)
            mbwi[~mask] = RobustScaler(copy=False).fit_transform(mbwi[~mask].reshape(-1, 1)).reshape(-1)
            mbwi[~mask] = MinMaxScaler(feature_range=(-1, 1), copy=False).fit_transform(mbwi[~mask].reshape(-1, 1)) \
                .reshape(-1)
            mask = np.isinf(mbwi) | np.isnan(mbwi) | mask
            mbwi = np.ma.array(mbwi, mask=mask, fill_value=-9999)
            return mbwi, mask

        @staticmethod
        #check if the list contains the required bands
        def listify(lst, uniques=[]):
            # pdb.set_trace()
            for item in lst:
                if isinstance(item, list):
                    uniques = listify(item, uniques)
                else:
                    uniques.append(item)
            return uniques.copy()
        ############################################ DWImageClustering ############################################
        ############################################ run_detect_water #############################################
        #Transform the rasters in a matrix where each band is a column
        @staticmethod
        def bands_to_columns(bands,invalid_mask):
            """
            Convert self.bands to a column type matrix where each band is a column
            It follows the order of the keys ordered
            :return : column type matrix
            """
            data = None
            for key in sorted(bands.keys()):
                band_array = bands[key]

                band_as_column = band_array[~invalid_mask].reshape(-1,1)

                if (key == 'Mir') or (key == 'Mir2') or (key == 'Nir') or (key == 'Nir2') or (key == 'Green'):
                    band_as_column = band_as_column * 4
                    band_as_column[band_as_column > 4] = 4

                data = band_as_column if data is None else np.concatenate([data, band_as_column], axis=1)
            return data

        # if algorithm is not kmeans,split data for a smaller ser (for performnce purposes)
        @staticmethod
        def get_train_test_split(data,train_size,min_train_size,max_train_size):
            """
            Split the provided data in train-test bunches
            :param min_train_size : minimum data quantity for train set
            :param max_train_size : maximum data quantity for train set
            :param train_size     : percentage of the data to be used as train dataset
            :param data           : data to be split
            :return               : train and test datasets
            """
            dataset_size = data.shape[0]

            if (dataset_size * train_size) < min_train_size:
                train_size = min_train_size / dataset_size
                train_size = 1 if train_size > 1 else train_size

            elif (dataset_size * train_size) > max_train_size:
                train_size = max_train_size / dataset_size
            
            return train_test_split(data, train_size=train_size)
        
        #create data bunch only with the bands used for clustering
        @staticmethod
        def split_data_by_bands(bands,data, selected_keys):
            """
            Gets data in column format (each band is a column) and returns only the desired bands
            :param data          : data in column format
            :param selected_keys : bands keys to be extracted
            :return              : data in column format only with the selected bands
            """
            bands_index = []
            bands_keys = list(sorted(bands.keys()))

            for key in selected_keys:
                bands_index.append(bands_keys.index(key))
            return data[:, bands_index]
        
    
        def find_best_k(self,data):
            """
            Find the best number of clusters according to an metrics.
            :param data : data to be tested
            :return     : number of clusters
            """
            # print('min_k :',self.min_k)
            # print('max_k :',self.max_k)
            # print('score_index :',self.score_index)
            # print(data)

            if self.min_k == self.max_k:
                print('Same number for minimum and maximum clusters: k = {}'.format(self.min_k))
                best_k = self.min_k
                return best_k

            # if score_index == 'silhouette':
            #     print('Selection of best number of clusters using Silhouete Index:')
            # else:
            #     print('Selection of best number of clusters using Calinski-Harabasz Index:')

            # if self.score_index == 'silhouette':
            #     print('score_index --> Silhouete')
            # else:
            #     print('score_index --> Calinski_harabaz')

            computed_metrics = []
            for num_k in range(self.min_k, self.max_k + 1):
                # cluster_model = cluster.KMeans(n_clusters=num_k, init='k-means++')
                cluster_model = cluster.AgglomerativeClustering(n_clusters=num_k, linkage=self.linkage)

                labels = cluster_model.fit_predict(data)

                if self.score_index == 'silhouette':
                    computed_metrics.append(metrics.silhouette_score(data, labels))
                    # print('k = {} index : {}'.format(num_k, computed_metrics[num_k - self.min_k]))

                else:
                    computed_metrics.append(calinski_harabasz_score(data, labels))
                    # print('k = {} index : {}'.format(num_k, computed_metrics[num_k - self.min_k]))

            best_k = computed_metrics.index(max(computed_metrics)) + self.min_k
            # print("best_k :",best_k)

            return best_k
        
        #apply the clusterization algorithm and return labels and train dataset
        @staticmethod
        def apply_cluster(data,best_k):
            """
            Apply the cluster algorithm to the data. Number of cluster is in self.best_k
            :param data  : data to be clustered
            :return      : Vector with the labels
            """
            clustering_method = 'agglomerative'
            if clustering_method == 'kmeans':
                cluster_model = cluster.KMeans(n_clusters=best_k, init='k-means++')
            elif clustering_method == 'gauss_mixture':
                cluster_model = GMM(n_components=best_k, covariance_type='full')
            else:
                cluster_model = cluster.AgglomerativeClustering(n_clusters=best_k, linkage='average')

            cluster_model.fit(data)
            return cluster_model.labels_.astype('int8')
        
        #cals statistics for each cluster
        @staticmethod
        def calc_clusters_params(data, clusters_labels,best_k):
            """
            Calculate parameters for each encountered cluster.
            Mean, Variance, Std-dev
            :param data            : Clustered data
            :param clusters_labels : Labels for the data
            :return                : List with cluster statistics
            """
            clusters_params = []
            for label_i in range(best_k):
                # first slice the values in the indexed cluster
                cluster_i = data[clusters_labels == label_i, :]

                cluster_param = {'clusterid': label_i}
                cluster_param.update({'mean': np.mean(cluster_i, 0)})
                cluster_param.update({'variance': np.var(cluster_i, 0)})
                cluster_param.update({'stdev': np.std(cluster_i, 0)})
                cluster_param.update({'diffb2b1': cluster_param['mean'][1] - cluster_param['mean'][0]})
                cluster_param.update({'pixels': cluster_i.shape[0]})

                clusters_params.append(cluster_param)

            return clusters_params
        
        #detect the water cluster
        @staticmethod
        def detect_cluster(bands,clusters_params, param, logic, band1, band2=None):
            """
            Detects a cluster according to a specific metrics
            :param param : Which parameter to search (mean, std-dev, variance,  ...)
            :param logic : Max or Min
            :param band1 : The band related to the parameter
            :param band2 :
            :return      : Cluster object that satisfies the logic
            """
            # get the bands available in the columns
            available_bands = sorted(bands.keys())

            param_list = []
            if band1:
                idx_band1 = available_bands.index(band1)
            if band2:
                idx_band2 = available_bands.index(band2)

            # todo: fix the fixed values
            for clt in clusters_params:
                if param == 'diff':
                    if not idx_band2:
                        raise OSError('Two bands needed for diff method')
                    param_list.append(clt['mean'][idx_band1] - clt['mean'][idx_band2])

                elif param == 'value':
                    if (clt['pixels'] > 5): # and (clt['mean'][available_bands.index('Mir2')] < 0.25*4):
                        param_list.append(clt['mean'][idx_band1])
                    else:
                        param_list.append(-1)

            if logic == 'max':
                idx_detected = param_list.index(max(param_list))
            else:
                idx_detected = param_list.index(min(param_list))

            return clusters_params[idx_detected]
        
        def identify_water_cluster(self,detect_water_cluster,bands):
            """
            Finds the water cluster within all the clusters.
            It can be done using MNDWI, MBWI or Mir2 bands
            :return: water cluster object
            """
            if detect_water_cluster == 'maxmndwi':
                if 'mndwi' not in bands.keys():
                    raise OSError('MNDWI band necessary for detecting water with maxmndwi option')
                water_cluster = self.detect_cluster(bands,self.clusters_params,'value', 'max', 'mndwi')

            # elif detect_water_cluster == 'maxmbwi':
            #     if 'mbwi' not in bands.keys():
            #         raise OSError('MBWI band necessary for detecting water with maxmbwi option')
            #     water_cluster = detect_cluster(bands,clusters_params,'value', 'max', 'mbwi')

            # elif detect_water_cluster == 'minmir2':
            #     if 'mndwi' not in bands.keys():
            #         raise OSError('Mir2 band necessary for detecting water with minmir2 option')
            #     water_cluster = detect_cluster(bands,clusters_params,'value', 'min', 'Mir2')

            # elif detect_water_cluster == 'maxndwi':
            #     if 'ndwi' not in bands.keys():
            #         raise OSError('NDWI band necessary for detecting water with minmir2 option')
            #     water_cluster = detect_cluster(bands,clusters_params,'value', 'max', 'ndwi')

            # elif detect_water_cluster == 'minnir':
            #     water_cluster = detect_cluster(bands,clusters_params,'value', 'min', 'Nir')

            # else:
            #     raise OSError('Method {} for detecting water cluster does not exist'.
            #                     format(self.config.detect_water_cluster))

            return water_cluster
        
        @staticmethod
        def apply_naive_bayes(data, clusters_labels, clusters_data):
            """
            Apply Naive Bayes classifier to classify data
            :param data            : new data to be classified
            :param clusters_labels : labels for the reference data
            :param clusters_data   : reference data
            :return                : labels for the new data
            """
            # train a NB classifier with the data and labels provided
            model = GaussianNB()

            # print('Applying clusters based --> naive bayes classifier')
            # print('Cross_val_score:{}'.format(cross_val_score(model, clusters_data, clusters_labels)))

            model.fit(clusters_data, clusters_labels)

            # return the new predicted labels for the whole dataset
            return model.predict(data)
        
        
        def supervised_classification(self,data, train_data, clusters_labels):
            """
            Applies a machine learning supervised classification
            :param data            : new data to be classified
            :param train_data      : reference data
            :param clusters_labels : labels for the reference data
            :return                : labels for the new data
            """
            if self.classifier == 'SVM':
                clusters_labels = apply_svm(data, clusters_labels, train_data)
            elif self.classifier == 'MLP':
                clusters_labels = apply_mlp(data, clusters_labels, train_data)
            else:
                clusters_labels = self.apply_naive_bayes(data, clusters_labels, train_data)

            return clusters_labels.astype('int8')
        
        # after obtain the final labels,clip bands with superios limit
        # after obtainting the final labels,clip bands with inferior limit
        #create an cluster array based on the cluster result (water will be value1)
        @staticmethod
        def create_matrice_cluster(indices_array,bands,clusters_labels,water_cluster,best_k):
            """
            Recreates the matrix with the original shape with the cluster labels for each pixel
            :param indices_array : position of the clustered pixels in the matrix
            :return              : clustered image (0-no data, 1-water, 2, 3, ... - other)
            """
            # create an empty matrix
            matrice_cluster = np.zeros_like(list(bands.values())[0]).astype('int8')

            # apply water pixels to value 1
            matrice_cluster[indices_array[0][clusters_labels == water_cluster['clusterid']],
                            indices_array[1][clusters_labels == water_cluster['clusterid']]] = 1

            # print('Assgnin 1 to cluster_id {}'.format(water_cluster['clusterid']))

            # loop through the remaining labels and apply value >= 3
            new_label = 2
            for label_i in range(best_k):

                if label_i != water_cluster['clusterid']:
                    matrice_cluster[indices_array[0][clusters_labels == label_i],
                                    indices_array[1][clusters_labels == label_i]] = new_label

                    new_label += 1
                else:
                    pass
                    # print('Skipping cluster_id {}'.format(label_i))

            return matrice_cluster


        ################################################ waterdetection #################################################
        def waterdetect(self):
            """
            waterdetection
            :return : watermask
            """
            ## wd.DWImageClustering
            # get the first band as reference of size
            ref_band = list(self.bands.keys())[0]
            ref_shape = self.bands[ref_band].shape

            #check the invalid_mask
            invalid_mask = np.zeros(ref_shape,dtype=bool)
            
            #check if the MNDWI index is necessary and if it exists
            if 'mndwi' in self.required_indices and 'mndwi' not in self.bands:
                mndwi,mndwi_mask = self.calc_normalized_difference(self.bands['Green'],self.bands['Mir2'],invalid_mask)
                invalid_mask |= mndwi_mask
                self.bands.update({'mndwi':mndwi})

            #check if the NDWI index exist
            if 'ndwi' in self.required_bands and 'ndwi' not in self.bands.keys():
                ndwi,ndwi_mask = self.calc_normalized_difference(self.bands['Green'],self.bands['Nir'],invalid_mask)
                invalid_mask |= ndwi_mask
                self.bands.update({'ndwi':ndwi})

            #check if the MBWI index exist
            if 'mbwi' in self.required_bands and 'mbwi' not in self.bands.keys():
                mbwi,mbwi_mask = self.calc_mbwi(self.bands,3,invalid_mask)
                invalid_mask |= mbwi_mask

            #check if the list contains the required bands
            for band in self.listify(self.bands_keys):
                if band == 'otsu' or band == 'canny':
                    continue
                if band not in self.bands.keys():
                    raise OSError('Band {}, not available in the dictionary'.format(self.band))
                if type(self.bands[band]) is not np.ndarray:
                    raise OSError('Band {} is not a numpy array'.format(self.band))
                if ref_shape != self.bands[band].shape:
                    raise OSError('Bands {} and {} with different size in clustering core'.format(self.band, ref_band))
                else:
                    pass
                    # print("band : ",band+"In require bands list")

            ## run_detect_water
            # print('My.DataComponent : self.bands_keys[0] :',self.bands_keys[0])
            #if passed options,override the existing options
            if self.bands_keys[0] == 'otsu':
                cluster_matrix = self.apply_otsu_treshold()
            elif self.bands_keys[0] == 'canny':
                cluster_matrix = self.apply_canny_treshold()
            elif False:
                cluster_matrix = None

            #Transform the rasters in a matrix where each band is a column
            data_as_columns = self.bands_to_columns(self.bands,invalid_mask)

            # two line vectors indicating the indexes (line column) of valid pixels
            ind_data = np.where(~invalid_mask)   

            # if algorithm is not kmeans,split data for a smaller ser (for performnce purposes)
            if self.clustering_method == 'kmean':
                train_data_as_columns=data_as_columns
            else:
                train_data_as_columns,ts= self.get_train_test_split(data_as_columns,self.train_size,self.min_train_size,self.max_train_size)

            #split1
            split_train_data_as_columns = self.split_data_by_bands(self.bands,train_data_as_columns,self.bands_keys)
            #split2
            split_data_as_columns = self.split_data_by_bands(self.bands,data_as_columns,self.bands_keys)

            #find best_k
            best_k = self.find_best_k(split_train_data_as_columns)

            #apply the clusterization algorithm and return labels and train dataset
            train_clusters_labels = self.apply_cluster(split_train_data_as_columns,best_k)

            #cals statistics for each cluster
            self.clusters_params = self.calc_clusters_params(train_data_as_columns,train_clusters_labels,best_k)

            #detect the water cluster
            water_cluster = self.identify_water_cluster(self.detect_water_cluster,self.bands)

            if self.clustering_method != 'kmeans':
                clusters_labels = self.supervised_classification(split_data_as_columns,split_train_data_as_columns,train_clusters_labels)
            else:
                clusters_labels = train_clusters_labels
            # print('My.DataComponent : clusters_labels :',clusters_labels)
            # after obtain the final labels,clip bands with superios limit
            for band,value in zip(self.clip_band,self.clip_sup_value):
                if value is not None:
                    if self.glint_mode and self.glint_processor is not None:
                        print('0')
                    else:
                        comp_array = value
                    clusters_labels[(clusters_labels == water_cluster['clusterid']) & (self.bands[band][~invalid_mask]>comp_array)] = -1
            #after obtainting the final labels,clip bands with inferior limit
            for band,value in zip(self.clip_band,self.clip_inf_value):
                if value is not None:
                    if self.glint_mode and self.glint_processor is not None:
                        print('0')
                    else:
                        comp_array = value
                    clusters_labels[(clusters_labels == water_cluster['clusterid']) & (self.bands[band][~invalid_mask]<comp_array)] = -1
            
            #create an cluster array based on the cluster result (water will be value1)
            cluster_matrix = self.create_matrice_cluster(ind_data,self.bands,clusters_labels,water_cluster,best_k)
            water_mask = np.where(cluster_matrix == 1,1,np.where(invalid_mask == 1,255,0)).astype('int8')
            watermask0 = water_mask==0
            watermask1 = water_mask==1
            return watermask1

        @staticmethod
        def apply_mask(array, mask, no_data_value=-9999, clear_nan=True):
            """
            Update mask
            :param array         : array of data
            :param mask          : mask
            :param no_data_value : 
            :param clear_nan     :
            :return              : Updated mask
            """
            if clear_nan:
                mask |= np.isnan(array) | np.isinf(array)
            return np.where(mask == True, -9999, array)

        @staticmethod
        def calc_param_limits(parameter, no_data_value=-9999,min_param_value=5,max_param_value = 20):
            """
            calulation min & max value by using percentile
            :param parameter       : ndarray data
            :param no_data_value   : no_data_value
            :param min_param_value : min_value
            :param max_param_value : max_value
            :return                : min_value,max_value
            """
            valid = parameter[parameter != no_data_value]
            min_value = np.percentile(valid, 1) if min_param_value is None else min_param_value
            # min_value = np.quantile(valid, 0.25) if self.config.min_param_value is None else self.config.min_param_value
            max_value = np.percentile(valid, 75) if max_param_value is None else max_param_value
            # max_value = np.quantile(valid, 0.75) if self.config.max_param_value is None else self.config.max_param_value
            return max_value * 1.1, min_value * 0.8

        @staticmethod
        def gray2color_ramp(grey_array,min_value=0, max_value=20, colormap='viridis', limits=(0, 1)):
            """
            Convert a greyscale n-dimensional matrix into a rgb matrix, adding 3 dimensions to it for R, G, and B
            The colors will be mixed
            :param max_value  : Maximum value for the color ramp, if None, we consider max(grey)
            :param min_value  : Minimum value for the color ramp, if None, we consider min(grey)
            :param grey_array : greyscale vector/matrix
            :param color1     : Color for the minimum value
            :param color2     : Color for the mid value
            :param color3     : Color for the maximum value
            :param limits     : Final boundary limits for the RGB values
            :return           : Colored vector/matrix
            """

            cm = plt.get_cmap(colormap)
            # # normaliza dentro de min e max values
            grey_vector = (grey_array - min_value) / (max_value - min_value)

            # # cut the values outside the limits of 0 and 1
            grey_vector[grey_vector < 0] = 0
            grey_vector[grey_vector > 1] = 1

            # # Apply the colormap like a function to any array:
            colored_image = cm(grey_vector)

            return MinMaxScaler(limits).fit_transform(colored_image[:, 0:3])
        

        def reg_burn_area(self,red, green, blue, burn_in_array, color=None, min_value=None, max_value=None, colormap='viridis',
                        fade=1, uniform_distribution=False, no_data_value=-9999, valid_value=1, transp=0.0):
            """
            Burn in a mask or a specific parameter into an RGB image for visualization purposes.
            The burn_in_array will be copied where values are different from no_data_value.
            :param uniform_distribution : convert the input values in a uniform histogram
            :param colormap             : matplotlib colormap (string) to create the RGB ramp
            :param max_value            : maximum value
            :param min_value            : minimum value
            :param red                  : Original red band
            :param green                : Original green band
            :param blue                 : Original blue band
            :param burn_in_array        : Values to be burnt in
            :param no_data_value        : Value to ne unconsidered
            :param color                : Tuple of color (R, G, B) to be used in the burn in
            :param fade                 : Fade the RGB bands to emphasize the copied values
            :param transp               : Transparency to use in the mask (0=opaque 1=completely transparent)
            :return                     : RGB image bands
            """
            if color:
                new_red = np.where(burn_in_array == valid_value, color[0] * (1 - transp) + red * (transp), red * fade)
                new_green = np.where(burn_in_array == valid_value, color[1] * (1 - transp) + green * (transp), green * fade)
                new_blue = np.where(burn_in_array == valid_value, color[2] * (1 - transp) + blue * (transp), blue * fade)
            else:
                # the mask is where the value equals no_data_value
                mask = (burn_in_array == no_data_value)
                
                # the valid values are those outside the mask (~mask)
                burn_in_values = burn_in_array[~mask]

                # apply scalers to uniform the data
                if uniform_distribution:
                    burn_in_values = QuantileTransformer().fit_transform(burn_in_values[:, np.newaxis])[:, 0]

                rgb_burn_in_values = self.gray2color_ramp(burn_in_values, min_value=min_value, max_value=max_value,
                                                    colormap=colormap, limits=(0, 1.))
                
                # return the scaled values to the burn_in_array
                burn_in_array[~mask] = rgb_burn_in_values[:, 0]
                burn_in_red = np.copy(burn_in_array)

                burn_in_array[~mask] = rgb_burn_in_values[:, 1]
                burn_in_green = np.copy(burn_in_array)

                burn_in_array[~mask] = rgb_burn_in_values[:, 2]
                burn_in_blue = np.copy(burn_in_array)

                # burn in the values
                new_red = np.where(burn_in_array == no_data_value, red*fade, burn_in_red)
                new_green = np.where(burn_in_array == no_data_value, green*fade, burn_in_green)
                new_blue = np.where(burn_in_array == no_data_value, blue*fade, burn_in_blue)
                
            return new_red, new_green, new_blue   

        @staticmethod
        def waterquality_fn(Red=1):
            """
            Turbidity and Suspended Particulate Matter (SPM) fuction
            SPM algorithm proposed by Nechad et al. (2010) https://www.sciencedirect.com/science/article/pii/S0034425714003654
            :param Red : Red band values
            :return    : float
            """
            a = 493.65
            b = 1.16
            c = 0.188
            tsm = a * Red / (1- (Red/c)) + b
            return tsm 

        ################################################ waterquality #################################################
        def waterquality(self,watermask=None,waterquality_function=None,range=None,colormap=None,bright=5,title='',label=''):
            """
            waterquality (Main fn)
            :param watermask             : water mask area that want to burn
            :param waterquality_function : operate function
            :param range                 : range of value
            :param colormap              : colormap that show 
            :param bright                : bright of saltellite image
            :param title                 : title of colorbar
            :param label                 : label of colorbar
            :return                      : R,G,B array
            """
            
            # Watermask
            if(watermask==None):
                self.watermask = self.waterdetect()
            else:
                self.watermask = watermask

            # Reference band , Prepare parameter
            if waterquality_function == None:
                parameter = self.waterquality_fn(self.bands['Red'])
            else: 
                parameter = waterquality_function(self.bands['Red'])  # fix : bands that the same with input function
            parameter = self.apply_mask(parameter,~self.watermask,-9999)
            
            # Min Max range value
            if range == None:
                self.max_value,self.min_value = self.calc_param_limits(parameter)
            else:
                self.min_value = range[0]
                self.max_value = range[1]

            # Color map 
            if colormap != None:
                cmap = plt.get_cmap(colormap)
            else:
                cmap = objearth.bluesea()

            # # Color bar
            # fig = plt.figure(figsize=(4,1))
            # ax1 = fig.add_axes([0.05,0.50,1.65,0.35])
            # norm = colors.Normalize(vmin=self.min_value,vmax=self.max_value)
            # cb1 = colorbar.ColorbarBase(ax1,cmap=cmap,norm=norm,orientation='horizontal')
            # ax1.set_title(title)
            # cb1.set_label(label)

            # Prepare RGB bands
            self.bright = bright
            red    = self.bands['Red']*self.bright
            green  = self.bands['Green']*self.bright
            blue   = self.bands['Blue']*self.bright

            #Clip value
            red[red>1]     = 1
            green[green>1] = 1
            blue[blue>1]   = 1

            # Apply function on the area
            red,green,blue = self.reg_burn_area(red=red,
                                green=green,
                                blue=blue,
                                burn_in_array=parameter,
                                color=None,
                                fade=1,
                                min_value=self.min_value,
                                max_value=self.max_value,
                                colormap=cmap,
                                uniform_distribution=False,
                                no_data_value=-9999)

            # plotshow Result
            rgb = np.stack([red,green,blue],axis=2)
            # objearth.plotshow(rgb)
            # plt.figure(figsize=(8,8))
            # plt.axis('off')
            # plt.imshow(rgb)
            
            # return red*10000,green*10000,blue*10000
            return rgb


class imagedataset(objearth,water):
    def __new__(cls,image_dataset):
        if (isinstance(image_dataset,xarray.Dataset) and 'time' in image_dataset.dims and image_dataset.dims['time']>1):
            instance = super().__new__(cls)
            print('Creating imageDataset object ...')
            return instance
        else:
            raise TypeError("image_dataset have to be xarray.Dataset and have more that 1 time")
    def __init__(self,image_dataset):
        """
        This class operator with Dataset
        :param command : xarray.Dataset
        """
        self.ids = image_dataset
        print("Done.")
    #
    def __str__(self):
        pass
    def detail(self):
        print(self.ids)
    def listtime(self):
        """
        list all time of data
        Return: int
        """
        # output_list = []
        rnd = self.ids.dims['time']
        for i in range(rnd):
            t = self.ids.isel(time=i).time.values
            print(t)
    def operator(self,command):
        """
        This function use for imagedataset operator with objearth function
        :param command : objearth function
        :return        : output_dict (specail type)
        """
        r = self.ids.dims['time']
        output_dict = {}
        for i in range(r):
            t = self.ids.isel(time=i).time.values
            eds = self.ids.isel(time=i)
            if command == 'truecolor':
                val = super().truecolor(eds)
            elif command == 'NDVI':
                val = super().NDVI(eds)
            elif command == 'NDMI':
                val = super().NDMI(eds)
            elif command == 'BSI':
                val = super().BSI(eds)
            elif command == 'EVI':
                val = super().EVI(eds)
            elif command == 'NDDI':
                val = super().NDDI(eds)
            elif command == 'NDWI':
                val = super().NDWI(eds)
            elif command == 'NMDI':
                val = super().NMDI(eds)
            elif command == 'waterdetect':
                val = water(eds).waterdetect()
            elif command == 'waterquality':
                val = water(eds).waterquality()
            else:
                print('Errro command')
                break
            # print(rgb)
            # 1 key
            key = 'key'+str(i)
            # 2.output_value (data)
            data=val
            # 3.output_data (label)
            label=t
            #output_dict
            output_dict.update({key:[data,label]})
        return output_dict
    def show(self,od,**z):
        r = self.ids.dims['time']
        for i in range(r):
            k = 'key'+str(i)
            if z:
                objearth.plotshow(od[k][0],figsize=(6,6),title=od[k][1],area=z['area'])
            else:
                objearth.plotshow(od[k][0],figsize=(6,6),title=od[k][1])
    def cloundcount(self,dataset,datarange=[352,480,944]):
        ds = dataset.pixel_qa
        s = xarray.where(ds==0,0,0)
        for j in datarange:
            x = xarray.where(ds==j,1,0)
            s = s + x
        count = (s!=0).sum()
        return int(count)
    def mincloud(self):
        a = []
        for i in range(self.ids.dims['time']):
            pc = self.cloundcount(self.ids.isel(time=i))
            a.append(pc)
        c = a.index(min(a))
        return self.ids.isel(time=c)










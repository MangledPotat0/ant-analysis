###############################################################################
#                                                                             #
#   Ant trajectory plotter for python3                                        #
#   Code written by Dawith Lim                                                #
#                                                                             #
#   Version: 1.4.4.0.3.2                                                      #
#   First written on 2019/11/14                                               #
#   Last modified: 2020/07/01                                                 #
#                                                                             #
#   Packages used                                                             #
#   -   argsparse: Argument parser to handle input parameters                 #
#   -   inspect: To check if the file exists.                                 #
#   -   math: Needed for the floor function in position binning.              #
#   -   matplotlib: pyplot is used to generate all the plots.                 #
#   -   numpy: Mainly needed for convenient array manipulation.               #
#   -   os: Relative file path finding.                                       #
#   -   trackpy: Soft matter tracking package. Used here primarily to call    #
#           the PandasHDFStoreBig function that just makes data handling      #
#           easier.                                                           #
#                                                                             #
###############################################################################

import argparse
import copy
import h5py
import inspect
import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import numpy as np
import os
import trackpy as tp

class AntProcessor:
    def __init__(self, argparser):
        self.jump = 1
        self.roll = 15
        self.plotres = 50
        self.boundary = False
        self.boundmin = 0
        self.boundmax = 18
        self.size = 18
        self.fps = 15
        self.density = True
        args = vars(argparser.parse_args())
        self.timebins = args['timebins']
        self.runtype = args['runtype']
        temppath = os.path.dirname(os.path.realpath(__file__))
        os.chdir(temppath)
        self.datapath = os.getcwd()
        self.filename = args['file']
        self.filepath = "../data/trajectories/"
        self.datafile = h5py.File('{}{}data.hdf5'.format(
            self.filepath,self.filename),'r')
        self.figpath = "../data/plots/{}/".format(self.filename)
        try:
            os.mkdir(self.figpath)
            print('Target directory not found; creating new directory.')
        except OSError:
            print('Directory {} already exists.'.format(self.figpath))
        print('File ready')
        print('Process initialized.')

    def get_angularvelocity(self,orientation):
    
        angularvelocity = np.empty(0)
        old = 0

        for th in orientation:
            angularvelocity = np.append(angularvelocity,th - old)
            old = th

        angularvelocity = np.array(angularvelocity[1:])

        return angularvelocity

    def get_displacement(self, position):

        trajectory = position
        length = len(trajectory)
        maxrange = 1000
        displacement = np.empty((length,maxrange))
        displacement.fill(np.nan)
        for n in range(length):
            terminate = 0
            for m in range(length - n):
                if terminate < maxrange:
                    displacement[n,m] = distance(trajectory[m+n]-trajectory[m])
                    terminate += 1

        return displacement

    def get_distance_to_boundary(self, position):
        dtb = np.empty(0)
        for coords in position:
            distance = math.sqrt((coords[0]-self.size/2)**2 + 
                    (coords[1]-self.size/2)**2)
            dtb = np.append(dtb,distance)
        
        return dtb

    def get_orientation(self, velocity):
        orientation = np.empty(0)
        for x in velocity:
            try:
                angle = math.atan2(x[0],x[1])
                orientation = np.append(orientation,angle)
            except:
                print('Math error')

        orientation = np.array(orientation)
    
        return orientation

    def get_position(self, dataset):
        pos = dataset[::self.jump,0:2]
        pos[pos==0] = np.nan

        x = rolling_average(pos[:,0],self.roll)
        y = rolling_average(pos[:,1],self.roll)
        zeros = np.where(x==0)
        x = np.delete(x,zeros)
        y = np.delete(y,zeros)
        position = np.array([(x-min(x))*self.size/(max(x)-min(x)),
            (y-min(y))*self.size/(max(y)-min(y))])
        return np.transpose(position)

    def get_velocity(self, position):
    
        velocity = np.empty((0,2))
        speed = np.empty(0)
        prev = [0,0]
        for positions in position:
            velocity = np.vstack((velocity, np.array([[positions[0] - prev[0],
                positions[1] - prev[1]]])))
            prev = positions
        velocity = velocity * self.fps
        for vel in velocity:
            speed = np.append(speed, np.sqrt(vel[0]**2 + vel[1]**2))
        velocity = np.delete(velocity, 0,axis=0)
        speed = np.delete(speed, 0)
        return velocity, speed

    def plot_angularvelocity_hist(self, angularvelocity, n):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.hist(angularvelocity,bins=np.linspace(-0.25*np.pi,
            0.25*np.pi,self.plotres), 
            label='Single ant speed',density=self.density)
        #ax.xaxis.set_major_formatter(tck.FormatStrFormatter('%g $\pi/12$'))
        #ax.xaxis.set_major_locator(tck.MultipleLocator(base=1/3))
        ax.set_xlabel('anglular velocity (rad/s)')
        ax.set_ylabel('frequency')
        plt.savefig('{}{}_angularvelocity_{}-{}.png'.format(self.figpath,
            self.filename,self.timebins,n))
        plt.close()

    def plot_displacement(self, displacement,n):
        avgs = np.nanmean(displacement, axis=1)
        plt.figure()
        plt.plot(avgs)
        plt.xlabel('t (s)')
        plt.ylabel('displacement (cm)')
        plt.savefig('{}{}_displacement_{}-{}.png'.format(self.figpath,
            self.filename,self.timebins,n))
        plt.close()

    def plot_orientation_hist(self, orientation, n):
        fig = plt.figure()
        ax = fig.add_subplot(111,projection='polar')
        ax.hist(orientation,bins=np.linspace(-math.pi,math.pi,self.plotres),
                label='Single ant speed',density=self.density)
        ax.set_ylabel('frequency')
        plt.savefig('{}{}_orientation_{}-{}.png'.format(self.figpath,
            self.filename,self.timebins,n))
        plt.close()

        return

    def plot_position_hist(self, position,n):
        position = np.transpose(position)
        plt.figure(figsize=(5.5,5.5))
        plt.hist2d(position[0],position[1],self.plotres,label=
                'Single ant position')
        plt.xlabel('x (cm)')
        plt.ylabel('y (cm)')
        plt.savefig('{}{}_2dhist_{}-{}.png'.format(self.figpath,
            self.filename,self.timebins,n))
        plt.close()

    def plot_speed(self, speed,n):
        speed = np.delete(speed,0) 
        time = np.arange(0,len(speed),1)
        plt.figure()
        plt.plot(time,speed)
        plt.xlabel('Time (frames)')
        plt.ylabel('Speed (m/s)')
        plt.savefig('{}{}_speed_{}-{}.png'.format(self.figpath,self.filename,
                    n,self.timebins))

    def plot_speed_hist(self, speed,n):
        speed = speed[speed<4]
        plt.figure()
        plt.hist(speed,bins=np.linspace(min(speed),max(speed),self.plotres),
                label='Single ant speed',density=self.density)
        plt.xlabel('Speed (cm/s)')
        plt.ylabel('frequency (frames)')
        plt.savefig('{}{}_speed_hist_{}-{}.png'.format(self.figpath,
                self.filename,self.timebins,n))
        plt.close()

        return
    
    def plot_trajectory(self, position,n):
        plt.figure(figsize=(5.5,5.5))
        position = np.transpose(position)
        plt.plot(position[0],position[1])
        plt.savefig('{}{}_trajectory_{}-{}.png'.format(self.figpath,
                    self.filename,self.timebins,n))
        plt.xlabel('x (cm)')
        plt.ylabel('y (cm)')
        plt.close()

    def plot_orient_vs_dist_from_center(self, data1, data2, n):
        fig = plt.figure()
        ax = fig.add_subplot(111,polar=True)
        ax.scatter(data1,data2, alpha=0.005)
        x = np.linspace(0,2*np.pi,360)
        y = np.full((360),9)
        ax.plot(x,y, 'r')
        #plt.scatter(data1,data2,alpha=0.05)
        ax.set_ylabel('Distance from center (cm)')
        #plt.xlabel('distance from center(cm)')
        plt.savefig('{}{}_radialdistance{}{}.png'.format(self.figpath,
                    self.filename,self.timebins,n))
        plt.close()

    def plot_dfc_vs_speed(self,dfc,speed,n):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(dfc,speed, alpha=0.002)
        ax.set_ylabel('Speed (cm/s)')
        ax.set_xlabel('Distance from center(cm)')
        plt.savefig('{}{}_dfcvsspeed{}{}.png'.format(self.figpath,
                    self.filename,self.timebins,n))
        plt.close()
    
    class Trajectory:
        def __init__(self, antproc, data):
            length = len(data)
            shape = np.array([length,2])
            self.position = antproc.get_position(data)
#            self.displacement = antproc.get_displacement(self.position)
            [self.velocity, self.speed] = antproc.get_velocity(self.position)
            self.orientation = antproc.get_orientation(self.velocity)
            self.angularvelocity = antproc.get_angularvelocity(self.orientation)
            self.disttoboundary = antproc.get_distance_to_boundary(self.position)[2:]
            self.position = self.position[2:]
            self.velocity = self.velocity[1:]
            self.speed = self.speed[1:]
            self.orientation = self.orientation[1:]
    
        def make_indices(self, data, criteria):
            minthresh,maxthresh = criteria
            truthfunction = ((data[:,0] > minthresh) & (data[:,0] < maxthresh)
                    ) & ((data[:,1] > minthresh) & (data[:,1] < maxthresh))
            self.indices = np.broadcast_to(truthfunction, len(data))

def distance(pair):
    x,y = pair
    output = math.sqrt(x**2 + y**2)
    return output 

def rolling_average(source, count):
    try:
        source = np.ma.masked_array(source,np.isnan(source))
        output = np.cumsum(source.filled(0))
        output[count:] = output[count:] - output[:-count]
        counts = np.cumsum(~source.mask)
        counts[count:] = counts[count:] - counts[:-count]
        counts[counts==0] = 1
        try:
            with np.errstate(invalid='ignore',divide='ignore'):
                output = output/counts
        except RuntimeWarning:
            print('zero or something')
    except:
        output = source
    return output

def main():
    
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', '--file', required=True, help=
                'Name for .hdf5 data file')
    argparser.add_argument('-t', '--timebins', required=True, help=
                'Number of time bins', type=int)
    argparser.add_argument('-r', '--runtype', required=True, help='Run type',
                type=str)
    ap = AntProcessor(argparser)
    
    trajectories = np.array([])
    
    ct = 1
    for setname in ap.datafile: 
        dataset = ap.datafile[setname]
        trajectories = np.append(trajectories, ap.Trajectory(ap, 
                                 dataset[1:]))
        trajectories[-1].make_indices(trajectories[-1].position,
                [ap.boundmin,ap.boundmax])
        if ap.runtype == 's':
            for t in range(ap.timebins):
                length=len(trajectories[-1].position)
                binsize=math.floor(length/ap.timebins)
                start = t*binsize
                end = (t+1)*binsize - 1
                indices = np.empty((len(trajectories[-1].position)),dtype=bool)
                indices.fill(False)
                if ap.boundary:
                    trajectories[-1].indices = ~trajectories[-1].indices
                indices[start:end] = trajectories[-1].indices[start:end]
                ap.plot_trajectory(trajectories[-1].position[indices],t+1)
                ap.plot_position_hist(trajectories[-1].position[indices],t+1)
                ap.plot_speed(trajectories[-1].speed[indices[1:]],t+1)
                ap.plot_speed_hist(trajectories[-1].speed[indices[1:]],t+1)
                ap.plot_orientation_hist(trajectories[-1].orientation[indices[
                                1:]],t+1)
                ap.plot_angularvelocity_hist(trajectories[-1].angularvelocity
                            [indices[2:]],t+1)
    
    if ap.runtype =='p':
        pool = copy.deepcopy(trajectories[-1])
        for t in range(ap.timebins):
            pool.position = np.empty((0,2))
            pool.disttoboundary = np.empty(0)
            pool.speed = np.array([])
            pool.orientation = np.array([])
            pool.angularvelocity = np.array([])
            for traj in trajectories:
                traj.make_indices(traj.position,[ap.boundmin,ap.boundmax])
                length=len(traj.position)
                binsize=math.floor(length/ap.timebins)
                start = t*binsize
                end = (t+1)*binsize - 1
                indices = np.empty(length,dtype=bool)
                indices.fill(False)
                if ap.boundary:
                    trajectories[-1].indices = ~trajectories[-1].indices[:]
                indices[start:end] = traj.indices[start:end]
                pool.position = np.vstack((pool.position, 
                    traj.position[indices]))
                pool.disttoboundary = np.append(pool.disttoboundary, 
                        traj.disttoboundary[indices])
                pool.speed = np.append(pool.speed, 
                        traj.speed[indices],axis=0)
                pool.orientation = np.append(pool.orientation, 
                        traj.orientation[indices],axis=0)
                pool.angularvelocity = np.append(pool.angularvelocity, 
                        traj.angularvelocity[indices],axis=0)

            ap.plot_position_hist(pool.position,t+1)
            ap.plot_speed_hist(pool.speed,t+1)
            ap.plot_orientation_hist(pool.orientation,t+1)
            ap.plot_angularvelocity_hist(pool.angularvelocity,t+1)
            ap.plot_orient_vs_dist_from_center(pool.orientation,
                    pool.disttoboundary,t+1)
            ap.plot_dfc_vs_speed(pool.disttoboundary,pool.speed,t+1)
#        pool.displacement = np.empty((2,18014))
#        for traj in trajectories:
#            pool.displacement = np.append(pool.displacement,traj.displacement,axis=1)
#        ap.plot_displacement(pool.displacement,0)
                    

    print('Process exited normally.')

if __name__ == '__main__':
    main()

# Put in as subclass to antprocessor


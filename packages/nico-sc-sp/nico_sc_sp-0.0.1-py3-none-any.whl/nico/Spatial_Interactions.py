
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, ConvexHull,voronoi_plot_2d, Delaunay

from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression,LogisticRegressionCV
from sklearn.model_selection import RandomizedSearchCV,GridSearchCV,cross_val_predict, cross_val_score,RepeatedStratifiedKFold,StratifiedShuffleSplit
from sklearn.metrics import make_scorer,accuracy_score, f1_score, classification_report,confusion_matrix,roc_curve, roc_auc_score, precision_score, recall_score, precision_recall_curve
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline
#from sklearn.metrics import precision_recall_fscore_support as score
#from imblearn.over_sampling import SMOTE, SMOTEN,ADASYN, KMeansSMOTE, SVMSMOTE
from sklearn.utils import class_weight
from sklearn.metrics import roc_curve, auc

#Metrics
from sklearn.metrics import cohen_kappa_score
from sklearn.metrics import hamming_loss
from sklearn.metrics import log_loss
from sklearn.metrics import zero_one_loss
from sklearn.metrics import matthews_corrcoef

import pandas as pd
import numpy as np
import seaborn as snn
import os
import random
import warnings
import time
#import pickle5 as pickle
from scipy.cluster.hierarchy import dendrogram, linkage
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import networkx as nx

warnings.filterwarnings('ignore')
#export PYTHONWARNINGS='ignore:Multiprocessing-backed parallel loops:UserWarning'
os.environ["PYTHONWARNINGS"] = "ignore::UserWarning"





def create_directory(outputFolder):
    answer=os.path.isdir(outputFolder)
    if answer==True:
        pass
    else:
        os.mkdir(outputFolder)



def findNeighbors_in_given_radius(location,radius):
    n=location.shape[0]
    #print('ss',location.shape)
    neighbor={}
    for i in range(n):
        loc1=location[i]
        #print(loc1)
        t1=(loc1[0]-1.1*radius) <= location[:,0]
        t2=location[:,0] <= (loc1[0]+1.1*radius)
        t3=(loc1[1]-1.1*radius) <= location[:,1]
        t4=location[:,1] <= (loc1[1]+1.1*radius)
        t5=(loc1[2]-1.1*radius) <= location[:,2]
        t6=location[:,2] <= (loc1[2]+1.1*radius)

        index=  np.where ( t1 & t2 & t3 & t4 & t5 & t6    )

        #print(index[0])
        #neighborIndex= index[0].remove(i)
        #print( neighborIndex)

        #fw=open('ankit'+str(i),'w')
        #for k in range(len(t1)):
        #    fw.write(str(location[k])+'\t'+str(t1[k])+'\t'+str(t2[k])+'\t'+str(t3[k])+'\t'+str(t4[k])+'\n')

        #for j in range(i+1,n):
        count=0

        for k in range(len(index[0])):
            j=index[0][k]
            if j!=i:
                count+=1
                loc2=location[j]
                dist=euclidean_dist(loc1,loc2)
                if dist<radius:
                    if i not in neighbor:
                        neighbor[i]=[j]
                    else:
                        if j not in neighbor[i]:
                            neighbor[i].append(j)

                    if j not in neighbor:
                        neighbor[j]=[i]
                    else:
                        if i not in neighbor[j]:
                            neighbor[j].append(i)

        #print('t',count,len(index[0]))


    newneig=[]
    avg_neigh=0.0
    for i in range(n):
        try:
            l=neighbor[i]
        except KeyError:
            l=[]
        #print(l)
        newneig.append(l)
        avg_neigh+=len(l)

    print('average neighbors:',avg_neigh/n)

    return newneig


def find_neighbors(pindex, triang):
    return triang.vertex_neighbor_vertices[1][triang.vertex_neighbor_vertices[0][pindex]:triang.vertex_neighbor_vertices[0][pindex+1]]


def create_spatial_CT_feature_matrix(radius,PP,louvain,noct,fraction_CT,saveSpatial):

    if radius==0:
        value=np.sum(PP,axis=0)
        if (PP.shape[1]==3)&(value[2]==0):
            PP=PP[:,[0,1]]
        tri = Delaunay(PP)
        newneig=[]
        avg_neigh=0.0
        for i in range(len(PP)):
            ol = find_neighbors(i,tri)
            l=[]
            temp=[]
            for j in range(len(ol)):
                dist=euclidean_dist(PP[i],PP[ol[j]])
                temp.append(dist)
                if dist<100:
                    l.append(ol[j])
                #print(i,j,dist,PP[i],PP[l[j]])
            #print(PP[i,l)
            #if len(l)!=len(ol):
            #    print(i,type(ol),ol,l,temp,'\n')
            newneig.append(l)
            avg_neigh+=len(l)

        print('average neighbors:',avg_neigh/len(PP))
        neighbors=newneig

    else:
        neighbors=findNeighbors_in_given_radius(PP,radius)
    n=len(neighbors)

    outputFilename=saveSpatial+'normalized_spatial_neighbors_'+str(radius)+'.dat'

    fw=open(outputFilename,'w')
    expectedNeighbors=[]
    #print(noct)
    for i in range(n):
        cell1=i
        CT1=louvain[i,0]
        V=neighbors[i]
        CT2=np.zeros(len(noct),dtype=float)
        for j in range(len(V)):
            name=louvain[V[j],0]
            try:
                CT2[name]+=1.0
            except KeyError:
                pass
        fw.write(str(cell1)+'\t'+str(CT1))
        expected=np.array(fraction_CT)*np.sum(CT2)
        tt=CT1
        #print(np.concatenate(np.array(celltype[key]),CT2))
        expectedNeighbors.append(np.concatenate([np.asarray([tt]),CT2]))
        #print(expectedNeighbors)
        CT2=CT2/expected   #np.sum(CT2) #np.linalg.norm(CT2)
        for j in CT2:
            fw.write('\t'+'%0.5f'%j)
        fw.write('\n')

    expectedNeighbors=np.array(expectedNeighbors)

    M=[]
    for i in range(len(noct)):
        a=np.where(expectedNeighbors[:,0]==i)
        b=np.where(expectedNeighbors[:,0]!=i)
        #print('a',len(a[0]),len(b[0]))
        myCT=np.mean(expectedNeighbors[a[0],1:],axis=0)
        remainCT=np.mean(expectedNeighbors[b[0],1:],axis=0)
        M.append(myCT/remainCT)
        #print(i,M[i])

    distance=[]
    for i in range(len(neighbors)):
        cc=louvain[i,0]
        p1=PP[i]
        temp=[]
        for j in range(len(neighbors[i])):
            nid=neighbors[i][j]
            nc=louvain[nid,0]
            p2=PP[nid]
            dist=euclidean_dist(p1,p2)
            #print(p1,p2,p1,nid,nc,dist)
            temp.append(dist)
            #print(i,cc,j,nid,p1,p2,dist)
        distance.append(temp)


    M=np.array(M)
    return M, neighbors,distance





def euclidean_dist(p1,p2):
    if len(p1)==2:
        value=np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 )
    if len(p1)==3:
        value=np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2  + (p1[2]-p2[2])**2)
    return value



def reading_data(positionFilename,clusterFilename,celltypeFilename,saveSpatial,delimiter,removed_CTs_before_finding_CT_CT_interactions):
    CTname=[]
    with open(celltypeFilename,'r') as f:
        cont = f.read()
        lines=cont.split('\n')
        CTname=[]
        CTid=[]
        for i in range(len(lines)):
            l=lines[i].split(delimiter)
            if len(l)>1:
                name=l[1].replace('/','_')
                name=name.replace(' ','_')
                name=name.replace('"','')
                name=name.replace("'",'')
                name=name.replace(')','')
                name=name.replace('(','')
                name=name.replace('+','p')
                name=name.replace('-','n')
                name=name.replace('.','')
                if name not in removed_CTs_before_finding_CT_CT_interactions:
                    CTname.append(name)
                    CTid.append(int(l[0]))


    df=pd.read_csv(clusterFilename)
    louvainFull=df.to_numpy()

    celltype={}
    cellsinCT={}
    index=[]
    for i in range(len(louvainFull)):
        clu_id=louvainFull[i][1]
        cel_id=louvainFull[i][0]
        if clu_id in CTid:
            index.append(i)
            #celltype[cel_id]=clu_id
            if clu_id not in cellsinCT:
                cellsinCT[clu_id]=[cel_id]
            else:
                cellsinCT[clu_id].append(cel_id)

    louvain=louvainFull[index,:]

    df=pd.read_csv(positionFilename,header=None)
    points=df.to_numpy()
    #need to sort the coordinates according to louvain order of cells
    temp={}
    for i in range(len(points)):
        temp[points[i,0]]=i

    index=[]
    for i in range(len(louvain)):
        id=louvain[i][0]
        index.append(temp[id])

    PP=points[index,:]

    #f=open('input_vizgen_liver_zcorrectCT/data/temp.dat','w')
    #for i in range(len(PP)):
    #    f.write(str(index[i])+'\t'+str(PP[i,1])+'\t'+str(PP[i,1])+'\n')
    #f.close()


    location_cellname2int={}
    location_int2cellname={}
    for i in range(len(PP)):
        name=PP[i,0]
        location_cellname2int[name]=i
        location_int2cellname[i]=name

    #for 2d system
    if PP.shape[1]==3:
        points=np.zeros((PP.shape[0],3),dtype=float)
        points[:,0]=PP[:,1]
        points[:,1]=PP[:,2]
        PP=points
        tissue_dim=2

    #for 3d system
    if PP.shape[1]==4:
        PP=PP[:,1:]
        tissue_dim=3


    #print('louvain',louvain.shape,PP.shape)

    noct=sorted(cellsinCT)
    actual_count=[]
    fraction_CT=[]
    for key in noct:
        actual_count.append(len(cellsinCT[key]))
        fraction_CT.append(len(cellsinCT[key])/float(len(louvainFull)))

    print('no of cell types',len(noct))

    temp=np.where(np.array(actual_count)>=5)
    good_index_cell_counts=temp[0]
    #print(actual_count,noct[good_index_cell_counts])

    less_no_cells_remove=[]
    for i in range(len(good_index_cell_counts)):
        index=np.where(louvain==noct[good_index_cell_counts[i]])
        less_no_cells_remove+=list(index[0])

    #print(less_no_cells[0:10],len(louvain))
    less_no_cells_remove=sorted(less_no_cells_remove)


    PP=PP[less_no_cells_remove]
    louvain=louvain[less_no_cells_remove]
    #print('louvain',louvain.shape,PP.shape)

    new_CT_id={}
    for i in range(len(good_index_cell_counts)):
        new_CT_id[noct[good_index_cell_counts[i]]]=i
    #print('a',np.unique(louvain))
    for i in range(len(louvain)):
        value=louvain[i,1]
        louvain[i,1]=new_CT_id[value]
        #print(value,louvain[i])

    fw=open(saveSpatial+'BiologicalNameOfCT.dat','w')
    for i in range(len(new_CT_id)):
            value=fraction_CT[good_index_cell_counts[i]]
            name=CTname[good_index_cell_counts[i]]
            #print(CTname[key], key, total,len(cellsinCT[key]))
            fw.write(str(i)+'\t'+name+'\t'+str('%0.4f'%value)+'\n')
    fw.close()

    louvainWithBarcodeId=louvain
    louvain=louvain[:,1:]

    return PP, louvain, noct,fraction_CT,louvainWithBarcodeId











def plot_multiclass_roc(clf, X_test, y_test, n_classes):
    y_score = clf.decision_function(X_test)
    # structures
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    # calculate dummies once
    y_test_dummies = pd.get_dummies(y_test, drop_first=False).values
    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_test_dummies[:, i], y_score[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])
    return fpr, tpr, roc_auc



def plot_results(maindir,nrow,ncol,nameOfCellType,radius,lambda_c,cmn,coef,classes,CTFeatures,x_test,x_train,predicted_probs,inputFeatures,BothLinearAndCrossTerms,inputdir,fpr, tpr, roc_auc):
    filename='R'+str(radius)
    #print(nameOfCellType)
    fig, ax = plt.subplots(nrow,ncol, figsize=(10, 7))
    plotaxis=[]
    for i in range(nrow):
        for j in range(ncol):
            plotaxis.append([i,j])


    highestROCofcelltype=[]
    for w in sorted(roc_auc, key=roc_auc.get, reverse=True):
        #print(w, roc_auc[w])
        highestROCofcelltype.append(w)


    #for i in range(len(classes)):
    '''
    for i in range(nrow*ncol):
        value=plotaxis[i]
        ax[value[0],value[1]].plot([0, 1], [0, 1], 'k--')
        ax[value[0],value[1]].set_xlim([0.0, 1.0])
        ax[value[0],value[1]].set_ylim([0.0, 1.05])
        if value[0]==(nrow-1):
            ax[value[0],value[1]].set_xlabel('False Positive Rate')
        else:
            ax[value[0],value[1]].set_xticks([])

        if i%ncol==0:
            ax[value[0],value[1]].set_ylabel('True Positive Rate')
        else:
            ax[value[0],value[1]].set_yticks([])

        ax[value[0],value[1]].set_title(str(highestROCofcelltype[i])+' : '+nameOfCellType[highestROCofcelltype[i]])
        ax[value[0],value[1]].plot(fpr[highestROCofcelltype[i]], tpr[highestROCofcelltype[i]], label='ROC(area = %0.2f)' % (roc_auc[highestROCofcelltype[i]]))

        ax[value[0],value[1]].legend(loc="best",fontsize=8)
        #ax[value[0],value[1]].grid(alpha=.4)
    snn.despine()
    #plt.suptitle('Receiver operating characteristic example')
    plt.tight_layout()
    plt.savefig(maindir+'ROC_'+filename+'.png')
    '''


    plt.figure(figsize=(12,10))
    classNames=[]
    for i in range(len(classes)):
        classNames.append(nameOfCellType[classes[i]])
    #print(classes,nameOfCellType,inputFeatures)
    snn.heatmap(cmn,annot=True, fmt='.2f',xticklabels=classNames, annot_kws={"size": 5},yticklabels=classNames)
    plt.xlabel('Predicted classes')
    plt.ylabel('Truth classes')
    plt.title('R = '+str(radius)+', C='+str(lambda_c))
    plt.tight_layout()
    plt.savefig(maindir+'Confusing_matrix_'+filename+'.png',dpi=300)

    plt.figure(figsize=(5,8))
    #plt.figure()
    #snn.set(font_scale=0.4)
    b=snn.heatmap(coef.transpose(),yticklabels=CTFeatures,xticklabels=classNames)
    #plt.xticks(rotation=90)
    _, ylabels= plt.yticks()
    b.set_yticklabels(ylabels, size = 5)

    if BothLinearAndCrossTerms==1:
        plt.ylabel('Features linear  terms')
    else:
        plt.ylabel('Features cross terms')
    #plt.xlabel('# of classes (no of cell types)')
    plt.title('R = '+str(radius)+', C='+str(lambda_c))
    plt.tight_layout()
    plt.savefig(maindir+'weight_matrix_'+filename+'.png',dpi=300)

    plt.figure(figsize=(12,6))

    plt.subplot(1,3,1)
    snn.heatmap(x_train,xticklabels=inputFeatures)
    plt.xlabel('# of input Features')
    plt.title('training set')
    plt.ylabel('75% of data')

    plt.subplot(1,3,2)
    snn.heatmap(x_test,xticklabels=inputFeatures)
    plt.xlabel('# of input Features')
    plt.title('testing set')
    plt.ylabel('25% of data')

    plt.subplot(1,3,3)
    snn.heatmap(predicted_probs,xticklabels=classes)
    plt.title('Predicted probability')
    plt.xlabel('# of classes (no of cell types)')
    plt.tight_layout()
    plt.savefig(maindir+'predicted_probability_'+filename+'.png')

    plt.close('all')
    #print(predicted_probs)
    #prob=sigmoid( np.dot([y_train, y_test,1], log_reg_model.coef_.T) + log_reg_model.intercept_ )
    #print(prob)


def read_processed_data(radius,inputdir):

    name=inputdir+'normalized_spatial_neighbors_'+str(radius)+'.dat'
    #data = np.loadtxt(name, delimiter=',', usecols=(), unpack=True)
    #data = np.loadtxt(open(path_to_data, "rb"), delimiter=",", skiprows=1, usecols=np.arange(1,n))
    data1 = np.genfromtxt(open(name, "rb"), delimiter='\t', skip_header=0)
    ind=~np.isnan(data1).any(axis=1)
    data=data1[ind,:]

    prop={}
    for i in range(len(data)):
        mytype=data[i,1]
        if mytype in prop:
            prop[mytype]+=1
        else:
            prop[mytype]=1

    #print('cell type proportion')
    total=sum(prop.values())
    keys=sorted( list( prop.keys())  )

    nct=len(prop)
    featureVector=range(2,2+nct) # #just neighborhood
    neighborhoodClass= data[:,featureVector]


    target= data[:,1]
    print('data shape',data.shape, target.shape, "neighbor shape",neighborhoodClass.shape)
    inputFeatures=range(nct)


    return neighborhoodClass,target,inputFeatures





def calculate_class_weights(vector):
    a=np.unique(vector)
    freq=[]
    for i in range(len(a)):
        freq.append(np.sum(vector==a[i]))

    total=np.sum(freq)
    cw={}
    for i in range(len(a)):
        cw[a[i]]=freq[i]/float(total)

    return cw







def model_log_regression(K_fold,n_repeats,neighborhoodClass,target,lambda_c,strategy,BothLinearAndCrossTerms,seed,n_jobs):
    polynomial = PolynomialFeatures(degree = BothLinearAndCrossTerms, interaction_only=True, include_bias=False)


    #hyperparameter_scoring='precision_weighted'
    #hyperparameter_scoring='f1_micro'
    #hyperparameter_scoring='recall_weighted'
    hyperparameter_scoring = {#'precision_weighted': make_scorer(precision_score, average = 'weighted'),
           #'precision_macro': make_scorer(precision_score, average = 'macro'),
           #'recall_macro': make_scorer(recall_score, average = 'macro'),
           #'recall_weighted': make_scorer(recall_score, average = 'weighted'),
           #'f1_macro': make_scorer(f1_score, average = 'macro'),
            #'log_loss':'neg_log_loss',
           'f1_weighted': make_scorer(f1_score, average = 'weighted')}

    parameters = {'C':lambda_c }

    if strategy=='L1_multi':
        log_reg_model = LogisticRegression(penalty='l1',multi_class='multinomial',class_weight='balanced',solver='saga',n_jobs=n_jobs)#very slow
    if strategy=='L1_ovr':
        log_reg_model = LogisticRegression(penalty='l1',multi_class='ovr',class_weight='balanced',solver='liblinear',n_jobs=n_jobs)
    if strategy=='L2_multi':
        log_reg_model = LogisticRegression(penalty='l2',multi_class='multinomial',class_weight='balanced',solver='lbfgs',n_jobs=n_jobs)
    if strategy=='L2_ovr':
        log_reg_model = LogisticRegression(penalty='l2',multi_class='ovr',class_weight='balanced',solver='lbfgs',n_jobs=n_jobs)
    if strategy=='elasticnet_multi':
        log_reg_model = LogisticRegression(penalty='elasticnet',multi_class='multinomial',class_weight='balanced',solver='saga',n_jobs=n_jobs)
        parameters = {'C':lambda_c, 'multi_class':['ovr','multinomial'], 'l1_ratio':np.linspace(0,1,10)  }
    if strategy=='elasticnet_ovr':
        log_reg_model = LogisticRegression(penalty='elasticnet',multi_class='ovr',class_weight='balanced',solver='saga',n_jobs=n_jobs)
        parameters = {'C':lambda_c, 'multi_class':['ovr','multinomial'], 'l1_ratio':np.linspace(0,1,10)  }


    #'''
    flag=1
    how_many_times_repeat={}
    while(flag):
        seed=seed+1
        sss = RepeatedStratifiedKFold(n_splits=K_fold, n_repeats=1 ,random_state=seed)
        gs_grid = GridSearchCV(log_reg_model, parameters, scoring=hyperparameter_scoring, refit='f1_weighted',cv=sss,n_jobs=n_jobs)
        #gs_random = RandomizedSearchCV(estimator=log_reg_model, param_distributions=parameters, scoring=hyperparameter_scoring, refit='f1_weighted',cv = sss,n_jobs=n_jobs)
        pipe_grid=Pipeline([  ('polynomial_features',polynomial),   ('StandardScaler',StandardScaler()), ('logistic_regression_grid',gs_grid)])
        #pipe_random=Pipeline([  ('polynomial_features',polynomial),   ('StandardScaler',StandardScaler()), ('logistic_regression_random',gs_random)])
        pipe_grid.fit(neighborhoodClass,target)
        #pipe_random.fit(neighborhoodClass,target)

        LR_grid= pipe_grid.named_steps['logistic_regression_grid']
        lambda_c=LR_grid.best_params_['C']
        if lambda_c not in how_many_times_repeat:
            how_many_times_repeat[lambda_c]=1
        else:
            how_many_times_repeat[lambda_c]+=1

        #LR_random= pipe_random.named_steps['logistic_regression_random']
        #if LR_grid.best_params_['C']==LR_random.best_params_['C']:
        #print('Searching hyperparameters ', 'Grid method:', LR_grid.best_params_['C'], ', Randomized method:', LR_random.best_params_['C'])
        print('Searching hyperparameters ', 'Grid method:', LR_grid.best_params_['C'])
        for key in how_many_times_repeat:
            if how_many_times_repeat[key]>1:
                flag=0
                print('Inverse of lambda regularization found', lambda_c)
    #'''
    #lambda_c=0.000244140625
    #lambda_c=0.0009765625




    scorecalc=[]
    for i in range(15):
        scorecalc.append([])

    cmn=[]
    coef=[]
    seed=seed+1
    sss = RepeatedStratifiedKFold(n_splits=K_fold, n_repeats=n_repeats ,random_state=seed)

    for train_index, test_index in sss.split(neighborhoodClass,target):
        x_train,x_test=neighborhoodClass[train_index],neighborhoodClass[test_index]
        y_train,y_test=target[train_index],target[test_index]


        if strategy=='L1_multi':
            log_reg_model = LogisticRegression(C=lambda_c,penalty='l1',multi_class='multinomial',class_weight='balanced',solver='saga',n_jobs=n_jobs)#very slow
        if strategy=='L1_ovr':
            log_reg_model = LogisticRegression(C=lambda_c,penalty='l1',multi_class='ovr',class_weight='balanced',solver='liblinear',n_jobs=n_jobs)
        if strategy=='L2_multi':
            log_reg_model = LogisticRegression(C=lambda_c,penalty='l2',multi_class='multinomial',class_weight='balanced',solver='lbfgs',n_jobs=n_jobs)
        if strategy=='L2_ovr':
            log_reg_model = LogisticRegression(C=lambda_c,penalty='l2',multi_class='ovr',class_weight='balanced',solver='lbfgs',n_jobs=n_jobs)
        if strategy=='elasticnet_multi':
            log_reg_model = LogisticRegression(C=lambda_c,penalty='elasticnet',multi_class='multinomial',l1_ratio=0.5,class_weight='balanced',solver='saga',n_jobs=n_jobs)
        if strategy=='elasticnet_ovr':
            log_reg_model = LogisticRegression(C=lambda_c,penalty='elasticnet',multi_class='ovr',l1_ratio=0.5,class_weight='balanced',solver='saga',n_jobs=n_jobs)

        pipe=Pipeline([  ('polynomial_features',polynomial),   ('StandardScaler',StandardScaler()), ('logistic_regression',log_reg_model)])

        pipe.fit(x_train, y_train)
        y_pred=pipe.predict(x_test)
        y_prob = pipe.predict_proba(x_test)

        log_metric=log_loss(y_test,y_prob)
        c_k_s=cohen_kappa_score(y_test,y_pred)
        zero_met=zero_one_loss(y_test,y_pred)
        hl=hamming_loss(y_test,y_pred)
        mcc=matthews_corrcoef(y_test,y_pred)

        scorecalc[0].append(pipe.score(x_test, y_test))
        #precision, recall, fscore, support = score(y_test, predicted)
        scorecalc[1].append(f1_score(y_test, y_pred, average="macro"))
        scorecalc[2].append(precision_score(y_test, y_pred, average="macro"))
        scorecalc[3].append(recall_score(y_test, y_pred, average="macro"))
        scorecalc[4].append(f1_score(y_test, y_pred, average="micro"))
        scorecalc[5].append(precision_score(y_test, y_pred, average="micro"))
        scorecalc[6].append(recall_score(y_test, y_pred, average="micro"))
        scorecalc[7].append(f1_score(y_test, y_pred, average="weighted"))
        scorecalc[8].append(precision_score(y_test, y_pred, average="weighted"))
        scorecalc[9].append(recall_score(y_test, y_pred, average="weighted"))
        scorecalc[10].append(c_k_s)
        scorecalc[11].append(log_metric)
        scorecalc[12].append(mcc)
        scorecalc[13].append(hl)
        scorecalc[14].append(zero_met)

        poly = pipe.named_steps['polynomial_features']
        LR= pipe.named_steps['logistic_regression']
        coef.append(LR.coef_)
        cmn.append(confusion_matrix(y_test,y_pred,normalize='true'))

    cmn_std=np.std(np.array(cmn),axis=0)
    coef_std=np.std(np.array(coef),axis=0)
    comp_score_std=np.std(np.array(scorecalc),axis=1)


    cmn=np.mean(np.array(cmn),axis=0)
    coef=np.mean(np.array(coef),axis=0)
    comp_score=np.mean(np.array(scorecalc),axis=1)

    print('training',x_train.shape,'testing',x_test.shape,'coeff',coef.shape)


    #cmn=confusion_matrix(y_test,y_pred,normalize='true')
    #cmn = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    classes=LR.classes_.astype(int)


    #modifiedFeatures=range(1,len(CTFeatures)+1)
    fpr, tpr, roc_auc=plot_multiclass_roc(pipe, x_test, y_test, n_classes=len(classes))

    CTFeatures=poly.get_feature_names_out()
    #print("Features", CTFeatures,type(CTFeatures))
    print("accuracy score\t",np.mean(scorecalc[0]))
    print("\nmacro")
    print("f1 score\t",np.mean(scorecalc[1]))
    print("precision score\t",np.mean(scorecalc[2]))
    print("recall score\t",np.mean(scorecalc[3]))

    print("\nmicro f1, precision, recall all same")
    print("score\t",np.mean(scorecalc[4]))
    #print("precision score in 10 run\t",np.mean(scorecalc[5]))
    #print("recall score in 10 run\t",np.mean(scorecalc[6]))

    print("\nWeighted")
    print("f1 score\t",np.mean(scorecalc[7]))
    print("precision\t",np.mean(scorecalc[8]))
    print("recall score\t",np.mean(scorecalc[9]))


    print('\ncohen_kappa_score (best=1): {0:.4f}'.format(np.mean(scorecalc[10])))
    print('log_loss or cross entropy (best=lowest): {0:.4f}'.format(np.mean(scorecalc[11])))
    print('matthews_corrcoef: {0:.4f}'.format( np.mean(scorecalc[12])  ))
    print('hemming_loss (best=lowest): {0:.4f}'.format( np.mean(scorecalc[13] )))
    print('zero_one_loss (best=0): {0:.4f}'.format(np.mean(scorecalc[14])))

    return cmn,coef,comp_score,cmn_std,coef_std,comp_score_std,classes, lambda_c,CTFeatures,x_test,x_train,y_prob ,fpr, tpr, roc_auc



def find_interacting_cell_types(cmn,coef,cmn_std,coef_std,confusion_cutoff,coeff_cutoff,CTFeatures,nameOfCellType,fw,filename,figuresize):


    a=np.diag(cmn)
    b=np.diag(cmn_std)
    goodPredictedCellType=np.argsort(-a)
    create_directory(filename)
    #for i in range(len(goodPredictedCellType)):
    #    print(i,a[goodPredictedCellType[i]])
    # top 3 cell type in confusion matrix
    for k in range(len(a)):
        if a[goodPredictedCellType[k]]>=confusion_cutoff:
            meanCoefficients=coef[goodPredictedCellType[k]]
            stdCoefficients=coef_std[goodPredictedCellType[k]]
            highestIndex=np.argsort(-abs(meanCoefficients))

            n=min(coeff_cutoff,len(highestIndex))
            coeff_of_CT=[]
            name_of_the_coeff=[]
            std_of_coeff=[]

            fw.write('\n'+str(k+1)+ ' Largest predicted cell type and their top 5 coefficients : '+
                    nameOfCellType[goodPredictedCellType[k]]+' ( id = '+str(goodPredictedCellType[k])+',  confusion score = '+str('%0.2f'%a[goodPredictedCellType[k]])+')\n')
            for i in range(n):
            #for i in range(len(highestIndex)):
                l=CTFeatures[highestIndex[i]].split()
                temp=''
                for j in range(len(l)):
                    temp+=nameOfCellType[int(l[j][1:])]
                    if j!=(len(l)-1):
                        temp+='--'
                #print(temp,highestIndex[i],CTFeatures[highestIndex[i]],goodCoefficients[ highestIndex[i]   ])
                integerName=CTFeatures[highestIndex[i]].replace('x','')
                fw.write(str(highestIndex[i])+'\t'+str('%0.2f'%meanCoefficients[ highestIndex[i]] ) +'\t'+temp+' ('+ integerName  +')\n')
                coeff_of_CT.append(meanCoefficients[ highestIndex[i]])
                name_of_the_coeff.append(temp)
                std_of_coeff.append(stdCoefficients[ highestIndex[i]])


            fig,ax=plt.subplots( figsize=(figuresize[0],figuresize[1]))
            xx=range(len(coeff_of_CT))
            yy=np.zeros((len(coeff_of_CT)))
            ax.errorbar(xx, coeff_of_CT, yerr=std_of_coeff,fmt='o',capsize=5)
            ax.plot(xx,yy,'k-',linewidth=0.2)
            ax.set_ylabel('value of coeff.')
            #ax.set_xlabel('name of the coeff.')
            titlename=nameOfCellType[goodPredictedCellType[k]]+', id = '+str(goodPredictedCellType[k])+', confusion score = {0:.3f}'.format(a[goodPredictedCellType[k]]) +'$\pm$'+str('%0.3f'%b[goodPredictedCellType[k]])
            ax.set_title(titlename,fontsize=7)


            ax.set_xticks(xx)
            ax.set_xticklabels(name_of_the_coeff)
            for tick in ax.get_xticklabels():
                tick.set_rotation(90)


            fig.tight_layout()
            fig.savefig(filename+'/Rank'+str(k+1)+'_'+nameOfCellType[goodPredictedCellType[k]],bbox_inches='tight',dpi=300)
            fig.clf()



def run_logistic_regression_on_spatial_features(inputdir,n_repeats,K_fold,coeff_cutoff,strategy,seed,n_jobs,lambda_c_ranges,BothLinearAndCrossTerms,radius,figuresize):
        f=open(inputdir+'BiologicalNameOfCT.dat')
        nameOfCellType={}
        for line in f:
            l=line[0:-1].split('\t')
            nameOfCellType[int(l[0])]=l[1]

        if BothLinearAndCrossTerms==1:
            maindir=inputdir+strategy+'_linear/'
        else:
            maindir=inputdir+strategy+'_cross/'

        create_directory(maindir)
        confusion_cutoff=0 # no of cell types wants to print

        fw=open(maindir+'prediction_R'+str(radius)+'.dat','w')
        fw.write('\nRadius = '+ str(radius)  + '\n')
        fname=maindir+'save_numpy_array_'+str(radius)+'.npz'


        flag=1
        if os.path.isfile(fname):
            filesize = os.path.getsize(fname)
            if filesize>0:
                data=np.load(fname,allow_pickle=True)
                coef=data['coef']
                cmn=data['cmn']
                cmn_std=data['cmn_std']
                coef_std=data['coef_std']
                CTFeatures=data['CTFeatures']
                find_interacting_cell_types(cmn,coef,cmn_std,coef_std,confusion_cutoff,coeff_cutoff,CTFeatures,nameOfCellType,fw,maindir+'/TopCoeff_R'+str(radius),figuresize)
                flag=0


        if flag==1:

                start_time = time.time()
                neighborhoodClass,target,inputFeatures=read_processed_data(radius,inputdir)
                cmn,coef,comp_score,cmn_std,coef_std,comp_score_std,classes,lambda_c,CTFeatures,x_test,x_train,predicted_probs,fpr, tpr, roc_auc=model_log_regression(K_fold, n_repeats,neighborhoodClass,target,lambda_c_ranges,strategy,BothLinearAndCrossTerms,seed,n_jobs)
                np.savetxt(maindir+'matrix_avg_coefficients_R'+str(radius)+'.dat', coef,fmt='%0.6f',delimiter=',')
                np.savetxt(maindir+'matrix_avg_confusion_R'+str(radius)+'.dat', cmn,fmt='%0.6f',delimiter=',')
                score=np.array([comp_score, comp_score_std]).T
                np.savetxt(maindir+'matrix_std_coefficients_R'+str(radius)+'.dat', coef_std,fmt='%0.6f',delimiter=',')
                np.savetxt(maindir+'matrix_std_confusion_R'+str(radius)+'.dat', cmn_std,fmt='%0.6f',delimiter=',')
                np.savetxt(maindir+'matrix_score_R'+str(radius)+'.dat',score ,fmt='%0.4f',delimiter=',')
                #np.savetxt(maindir+'matrix_Features'+str(radius)+'.dat',CTFeatures ,fmt='%s',delimiter=',')
                np.savez(maindir+'save_numpy_array_'+str(radius)+'.npz',cmn=cmn,coef=coef,cmn_std=cmn_std,coef_std=coef_std,CTFeatures=CTFeatures)

                find_interacting_cell_types(cmn,coef,cmn_std,coef_std,confusion_cutoff,coeff_cutoff,CTFeatures,nameOfCellType,fw,maindir+'/TopCoeff_R'+str(radius),figuresize)


                plot_results(maindir,2,3,nameOfCellType,radius,lambda_c,cmn,coef,classes,CTFeatures,x_test,x_train,predicted_probs,inputFeatures,BothLinearAndCrossTerms,inputdir,fpr, tpr, roc_auc)
                finish_time=time.time()

                fw.write('\n\nTotal time to compute = '+ str(finish_time-start_time)+'\n')
                print('time taken in sec', finish_time-start_time)

        fw.close()



def plot_evaluation_scores(inputRadius,BothLinearAndCrossTerms,inputdir,strategy,figuresize):
    if BothLinearAndCrossTerms==1:
        maindir=inputdir+strategy+'_linear/'
    else:
        maindir=inputdir+strategy+'_cross/'

    ## The order of all 15 scores are following
    #1-4 'accuracy','macro F1','macro precision','macro recall',
    #5-7 'micro [all]',
    #8-11 'weighted F1','weighted precision','weighted recall','cohen kappa',
    #12=15 'cross entropy', 'matthew correlation coefficient','heming loss', 'zero one loss'

    xlabels=['accuracy','macro F1','macro precision','macro recall','micro [all]','weighted F1','weighted precision','weighted recall','cohen kappa','mcc']
    index=[0,1,2,3,4,7,8,9,10,12]

    for radius in inputRadius:
        fig,axs=plt.subplots(1,1,figsize=(figuresize[0],figuresize[1]))
        name=maindir+'matrix_score_R'+str(radius)+'.dat'
        data=np.genfromtxt(open(name, "rb"), delimiter=',', skip_header=0)
        yt=data[index,0]
        xt=range(len(yt))
        axs.plot(xt,yt,'b.-',label=strategy)
        lowRg=yt-data[index,1]
        highRg=yt+data[index,1]
        axs.fill_between(xt, lowRg, highRg,facecolor='b',alpha=0.2)
        legend1= axs.legend(loc='lower left',bbox_to_anchor=(0.02, 0.05),ncol=1, borderaxespad=0., prop={"size":6},fancybox=True, shadow=True)

        axs.set_xticks(range(len(index)))
        ytstd=max(data[index,1])
        axs.set_yticks(np.linspace(min(yt)-ytstd,max(yt)+ytstd,4))

        axs.set_xticklabels(xlabels)
        for tick in axs.get_xticklabels():
            tick.set_rotation(90)

        axs.set_ylabel('score')
        fig.tight_layout()
        fig.savefig(maindir+'scores_'+str(radius)+'.png',bbox_inches='tight',dpi=300)
        fig.clf()



def plot_normalized_coefficients_radius_wise(inputRadius,BothLinearAndCrossTerms,inputdir,strategy,figuresize):
    f=open(inputdir+'BiologicalNameOfCT.dat')
    nameOfCellType={}
    featureName=[]
    for line in f:
        l=line[0:-1].split('\t')
        nameOfCellType[int(l[0])]=l[1]
        featureName.append(l[1])


    if BothLinearAndCrossTerms==1:
        maindir=inputdir+strategy+'_linear/'
    else:
        maindir=inputdir+strategy+'_cross/'

    savedir=maindir+"RadiusWiseNormalizedCoefficients/"
    create_directory(savedir)

    coef=[]
    confusion=[]
    for radius in inputRadius:
        fname=maindir+'save_numpy_array_'+str(radius)+'.npz'
        data=np.load(fname,allow_pickle=True)
        coef.append(data['coef'])
        cmn=data['cmn']
        #cmn_std=data['cmn_std']
        #coef_std=data['coef_std']
        CTFeatures=data['CTFeatures']
        #coef.append(np.loadtxt(maindir+'matrix_avg_coefficients_R'+str(radius)+'.dat',delimiter=','))
        #cmn=np.loadtxt(maindir+'matrix_avg_confusion_R'+str(radius)+'.dat',delimiter=',')
        confusion.append(np.diagonal(cmn))


    coefSize=coef[0].shape
    coef=np.array(coef)
    C=np.array(confusion)
    B=np.einsum('kij->ikj',coef)
    #print(B.shape,C.shape)


    name_of_the_coeff=[]
    n=coefSize[1]
    for i in range(n):
        l=CTFeatures[i].split()
        temp=''
        for j in range(len(l)):
            temp+=nameOfCellType[int(l[j][1:])]
            if j!=(len(l)-1):
                temp+='--'
        name_of_the_coeff.append(temp)


    for i in range(len(B)):
        fig,ax=plt.subplots(1,1,figsize=(figuresize[0],figuresize[1]))
        for j in range(len(B[i])):
            value=np.max(abs(B[i][j]))
            B[i][j]=B[i][j]/value
        snn.heatmap(B[i],xticklabels=name_of_the_coeff)#,xticklabels=classes)
        ax.set_yticklabels(inputRadius,fontsize=5, rotation=0)
        ax.set_xticklabels(name_of_the_coeff,fontsize=5, rotation=90)
        ax.set_title(featureName[i] + ' [%0.2f'%C[0,i] + ', %0.2f]'%C[-1,i]   ,fontsize=7)
        fig.tight_layout()
        fig.savefig(savedir+'CT_'+str(i+1)+ '_'+featureName[i]  + '.png',bbox_inches='tight',dpi=300)
        fig.clf()




def plot_niche_interactions(inputdir,strategy,BothLinearAndCrossTerms,radius,figuresize,niche_cutoff):
#def plot_niche_interactions(inputdir,n_repeats,K_fold,coeff_cutoff,strategy,seed,n_jobs,lambda_c_ranges,BothLinearAndCrossTerms,radius,figuresize):
        f=open(inputdir+'BiologicalNameOfCT.dat')
        nameOfCellType=[]
        for line in f:
            l=line[0:-1].split('\t')
            #nameOfCellType[int(l[0])]=l[1]
            nameOfCellType.append(l[1])

        if BothLinearAndCrossTerms==1:
            maindir=inputdir+strategy+'_linear/'
        else:
            maindir=inputdir+strategy+'_cross/'

        #create_directory(maindir)
        #confusion_cutoff=0 # no of cell types wants to print

        #fw=open(maindir+'prediction_R'+str(radius)+'.dat','w')
        #fw.write('\nRadius = '+ str(radius)  + '\n')
        fname=maindir+'save_numpy_array_'+str(radius)+'.npz'
        #print('fname',fname)
        flag=1
        if os.path.isfile(fname):
            filesize = os.path.getsize(fname)
            if filesize>0:
                data=np.load(fname,allow_pickle=True)
                coef=data['coef']
                cmn=data['cmn']
                cmn_std=data['cmn_std']
                coef_std=data['coef_std']
                CTFeatures=data['CTFeatures']

        #print(coef.shape,len(CTFeatures))

        '''
        meanCoefficients=coef[0]
        stdCoefficients=coef_std[0]
        #highestIndex=np.argsort(-abs(meanCoefficients))

        n=min(len(meanCoefficients))
        coeff_of_CT=[]
        name_of_the_coeff=[]
        std_of_coeff=[]


        for i in range(n):
            l=CTFeatures[i].split()
            temp=''
            for j in range(len(l)):
                temp+=nameOfCellType[int(l[j][1:])]
                if j!=(len(l)-1):
                    temp+='--'
        integerName=CTFeatures[i].replace('x','')
        coeff_of_CT.append(meanCoefficients[i])
        name_of_the_coeff.append(temp)
        std_of_coeff.append(stdCoefficients[i])
        '''
        #sklearn.cluster.bicluster
        linked=linkage(coef,'single')
        #plt.figure(figsize=(10, 7))
        fig,ax=plt.subplots( figsize=(figuresize[0],figuresize[1]))
        dendrogram(linked,
            orientation='top',
            labels=nameOfCellType,
            distance_sort='descending',
            show_leaf_counts=True)
        #ax.set_xticks(xx)
        #ax.set_xticklabels(name_of_the_coeff)
        for tick in ax.get_xticklabels():
            tick.set_rotation(90)

        fig.savefig(maindir+'HierarchicalClustering_Rad'+str(radius),bbox_inches='tight',dpi=300)
        fig.clf()






        n=len(nameOfCellType)
        top=cm.get_cmap('jet',n)
        newcmp=ListedColormap(top(np.linspace(0.95,0.15,n)),name="OrangeBlue")
        gradientColor=newcmp.colors
        #print(len(gradientColor),len(top))
        G = nx.DiGraph()
        #coef=coef[0:3,0:19]

        labeldict={}
        for i in range(len(nameOfCellType)):
            labeldict[i]=nameOfCellType[i]
            G.add_node(i,color=gradientColor[i])

        fig,ax=plt.subplots( figsize=(figuresize[0],figuresize[1]))
        edges=[]
        #print('coef',coef.shape, np.max(abs(coef)))
        norm_coef=coef/np.max(abs(coef))

        largest=[]
        for i in range(coef.shape[0]):
            for j in range(coef.shape[1]):
                if norm_coef[i,j]>niche_cutoff:
                    if i!=j:
                        #edges.append([i,j,coef[i,j]])
                        largest.append(norm_coef[i,j])
                        G.add_edge(j,i,color=gradientColor[i],weight=norm_coef[i,j])
                        #print(i,nameOfCellType[i],nameOfCellType[j],coef[i,j])

        #print(sorted(largest))

        #G.add_edges_from([(1, 2,10), (1, 3,20)])
        #G.add_weighted_edges_from(edges)


        '''
        #layout
        pos=nx.fruchterman_reingold_layout(G)
        pos=nx.circular_layout(G)
        pos=nx.random_layout(G)
        pos=nx.spectral_layout(G)
        pos=nx.spring_layout(G)
        '''

        edges = G.edges()
        colors = [G[u][v]['color'] for u,v in edges]
        weights = [G[u][v]['weight'] for u,v in edges]
        #ncolor=[G[u]['color'] for u in G.nodes()]

        #edge_labels = dict([((n1, n2), f'{n1}->{n2}') for n1, n2 in G.edges])
        edge_labels = dict([((n1, n2), '%0.2f'%G[n1][n2]['weight']) for n1, n2 in G.edges])

        pos = nx.nx_pydot.graphviz_layout(G)


        #pos=nx.spring_layout(G)
        #pos=nx.circular_layout(G)
        nx.draw(G, pos = pos,
        labels=labeldict,with_labels=True,node_size=500,
         linewidths=1, font_size=5, font_weight='bold',width=weights, edge_color=colors,node_color=gradientColor,
        )
        nx.draw_networkx_edge_labels(G, pos,edge_labels=edge_labels,label_pos=0.35, font_size=3  )

        #plt.show()


        fig.savefig(maindir+'DirectedGraph_Rad'+str(radius),bbox_inches='tight',dpi=300)
        fig.clf()

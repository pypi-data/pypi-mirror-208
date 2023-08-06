import scanpy as sc
import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np
import pandas as pd
import os
#import pickle
import math
import collections
import networkx as nx
from types import SimpleNamespace
from scipy.spatial import cKDTree
#from SCTransform import SCTransform

import warnings
import time
import seaborn as snn
from collections import Counter

#warnings.filterwarnings('ignore')
#export PYTHONWARNINGS='ignore:Multiprocessing-backed parallel loops:UserWarning'
#os.environ["PYTHONWARNINGS"] = "ignore::UserWarning"


def create_directory(outputFolder):
    answer=os.path.isdir(outputFolder)
    if answer==True:
        pass
    else:
        os.mkdir(outputFolder)


def find_index(sp_genename,sc_genename):
    index_sc=[]
    index_sp=[]
    d={}
    for j in range(len(sc_genename)):
        name=sc_genename[j]
        d[name]=j

    for i in range(len(sp_genename)):
        name=sp_genename[i]
        try:
            d[name]
            flag=1
        except KeyError:
            flag=0
        if flag==1:
            index_sc.append(d[name])
            index_sp.append(i)
    return index_sp,index_sc


def find_match_index_in_dist(t1,t2,s1,s2,index_1,index_2):
    for i in range(len(s1)):
        if s1[i]==index_1:
            p1=t1[i]
    for i in range(len(s2)):
        if s2[i]==index_2:
            p2=t2[i]
    return p1,p2


def find_mutual_nn(minkowski_order,data1, data2, sp_barcode,sc_barcode, k1, k2):
    print('I am here finding mutual nearest neighbor')

    #data1 is spatial
    #data2 is single
    #print(data1.shape,data2.shape)

    n_jobs=-1
    d1,k_index_1 = cKDTree(data1).query(x=data2, k=k1, p=minkowski_order,workers=n_jobs)
    d2,k_index_2 = cKDTree(data2).query(x=data1, k=k2, p=minkowski_order,workers=n_jobs)
    print(data1.shape,k_index_1.shape,'\t',data2.shape, k_index_2.shape)
    mutual_1 = []
    mutual_2 = []
    dist_1=[]
    dist_2=[]
    for index_2 in range(data2.shape[0]):
     t1=d1[index_2]
     s1=k_index_1[index_2]
     for index_1 in s1:
        t2=d2[index_1]
        s2=k_index_2[index_1]
        if index_2 in s2:
            p1,p2=find_match_index_in_dist(t1,t2,s1,s2,index_1,index_2)
            #print('a',temp1[index_1],temp2[index_2])
            mutual_1.append(index_1)
            mutual_2.append(index_2)
            dist_1.append(p1)
            dist_2.append(p2)
    #print(mutual_1,dist_1)

    a1=np.array(mutual_1)
    a2=np.array(mutual_2)
    dist_1=np.array(dist_1)
    dist_2=np.array(dist_2)
    a1=sp_barcode[a1]
    a2=sc_barcode[a2]
    a1=np.reshape(a1,(1,len(a1)))
    a2=np.reshape(a2,(1,len(a2)))
    dist_1=np.reshape(dist_1,(1,len(dist_1)))
    dist_2=np.reshape(dist_2,(1,len(dist_2)))
    b=np.concatenate((a1,a2,dist_1,dist_2)).T

    return b




def sct_return_sc_sp_in_shared_common_PC_space(ad_sp1,ad_sc1,no_of_pc,method):
    sct_ad_sc=ad_sc1.copy()
    sct_ad_sp=ad_sp1.copy()

    sc.pp.scale(sct_ad_sp, zero_center=True)
    sc.pp.scale(sct_ad_sc, zero_center=True)

    sc.pp.pca(sct_ad_sc,zero_center=None,n_comps=no_of_pc)
    sc_com_pc=sct_ad_sc.varm['PCs']

    tp_sc=str(type(sct_ad_sc.X))
    tp_sp=str(type(sct_ad_sp.X))
    if tp_sc=="<class 'scipy.sparse._csr.csr_matrix'>":
        msc=sct_ad_sc.X.toarray()
    else:
        msc=sct_ad_sc.X

    if tp_sp=="<class 'scipy.sparse._csr.csr_matrix'>":
        msp=sct_ad_sp.X.toarray()
    else:
        msp=sct_ad_sp.X


    msp=np.nan_to_num(msp)
    msc=np.nan_to_num(msc)
    transfer_sp_com = np.matmul(msp, sc_com_pc)
    transfer_sc_com = np.matmul(msc, sc_com_pc)




    for i in range(transfer_sp_com.shape[1]):
        mu1=np.mean(transfer_sp_com[:,i])
        svd1=np.std(transfer_sp_com[:,i])
        transfer_sp_com[:,i]= (transfer_sp_com[:,i]-mu1)/svd1

        mu2=np.mean(transfer_sc_com[:,i])
        svd2=np.std(transfer_sc_com[:,i])
        transfer_sc_com[:,i]= (transfer_sc_com[:,i]-mu2)/svd2
        #print(i,mu1,mu2,svd1,svd2)



    sc_barcode=sct_ad_sc.obs_names.to_numpy()
    sp_barcode=sct_ad_sp.obs_names.to_numpy()

    #print('sc',transfer_sc_com.shape,sc_cellname.shape)
    #print('sp',transfer_sp_com.shape,sp_cellname.shape)

    return transfer_sp_com, transfer_sc_com, sp_barcode,sc_barcode





def find_annotation_index(annot_cellname,sct_cellname):
    d={}
    for i in range(len(annot_cellname)):
        d[annot_cellname[i]]=i

    index=[]
    for i in range(len(sct_cellname)):
        index.append(d[sct_cellname[i]])

    return index




def find_commnon_MNN(input):
    print('I am in MNN')
    df=pd.read_csv(input.fname,header=None)
    #data contains 2 column files of sct_pairing_shared_common_gene_PC.csv
    # first column is MNN pairs of spatial and
    # second column is MNN pairs of single cell
    data=df.to_numpy()

    mnn_singlecell_matchpair_barcode_id=np.unique(data[:,1])
    mnn_spatial_matchpair_barcode_id=np.unique(data[:,0])

    # find the annotated indexes
    index_annot_sc=find_annotation_index(input.annotation_singlecell_barcode_id,mnn_singlecell_matchpair_barcode_id)
    index_annot_sp=find_annotation_index(input.annotation_spatial_barcode_id,mnn_spatial_matchpair_barcode_id )



    #There are many indexes for spatial and single cell data
    # 1) MNN single cell                    data[:,1]                                       90,876
    # 2) MNN unique                          mnn_singlecell_matchpair_id                    10,089
    # 3) SC transform cell id                input.sct_singlecell_barcode_id                18,754
    # 4) original matrix cell id             input.annotation_singlecell_barcode_id         185,894
    # 5) original cell type name            input.annotation_singlecell_celltypename        185,894
    # 6) MNN unique id in sct               mnn_singlecell_matchpair_barcode_id             10,089
    # 7) common index between 6 and 4       index_mnn_sc,index_annot_sc

    # 1) MNN spatial                        data[:,0]                                       90,876
    # 2) MNN unique                         mnn_spatial_matchpair_id                        8,932
    # 3) SC transform cell id               input.sct_spatial_barcode_id                    86,880
    # 4) original matrix cell id            input.annotation_spatial_barcode_id             395,215
    # 5) original cell type name            input.annotation_spatial_celltypename           395,215
    # 55) original spatial cluster id       input.annotation_spatial_cluster_id             395,215
    # 6) MNN unique id in sct               mnn_spatial_matchpair_barcode_id                8,932
    # 7) common index between 6 and 4       index_mnn_sp,index_annot_sp

    d_single_cluster={}
    for i in range(len(input.lsc[0])):
        singlecell_unique_clusterid=input.lsc[1][i]
        d_single_cluster[singlecell_unique_clusterid]=i

    d_spatial_cluster={}
    for i in range(len(input.lsp[0])):
        spatialcell_unique_clusterid=input.lsp[1][i]
        d_spatial_cluster[spatialcell_unique_clusterid]=i

    total_in_row=np.zeros((1,len(input.lsp[0])),dtype=float)
    total_in_col=np.zeros((1,len(input.lsc[0])),dtype=float)

    d_single={}
    for i in range(len(input.annotation_singlecell_cluster_id)):
        d_single[input.annotation_singlecell_barcode_id[i]]=input.annotation_singlecell_cluster_id[i]
        col=d_single_cluster[d_single[input.annotation_singlecell_barcode_id[i]]]
        total_in_col[0,col]+=1

    d_spatial={}
    for i in range(len(input.annotation_spatial_cluster_id)):
        d_spatial[input.annotation_spatial_barcode_id[i]]=input.annotation_spatial_cluster_id[i]
        spatialcell_cluid=d_spatial[input.annotation_spatial_barcode_id[i]]
        col=d_spatial_cluster[spatialcell_cluid]
        total_in_row[0,col]+=1


    mat21=np.zeros((len(input.lsc[0]),len(input.lsp[0])),dtype=float)
    mat22=np.zeros((len(input.lsp[0]),len(input.lsc[0])),dtype=float)
    mat1=np.zeros(  (1,len(input.lsc[0]) ) ,dtype=float)
    mat3=np.zeros(  (1,len(input.lsp[0]) ),dtype=float)


    unique_singlecell_barcode_in_MNN=np.unique(data[:,1])
    for i in range(len(unique_singlecell_barcode_in_MNN)):
        singlecell_cluid=d_single[unique_singlecell_barcode_in_MNN[i]]
        col=d_single_cluster[singlecell_cluid]
        #print(i,spatialcell_cluid)
        mat1[0,col]+=1


    #count how many anchor points matches to each spatial clusters
    unique_spatial_barcode_in_MNN=np.unique(data[:,0])
    for i in range(len(unique_spatial_barcode_in_MNN)):
        spatialcell_cluid=d_spatial[unique_spatial_barcode_in_MNN[i]]
        col=d_spatial_cluster[spatialcell_cluid]
        #print(i,spatialcell_cluid)
        mat3[0,col]+=1


    anchorFreqRow=mat3/total_in_row
    anchorFreqCol=mat1/total_in_col

    print("SC",total_in_col,np.sum(total_in_col))
    print("SP",total_in_row,np.sum(total_in_row))
    print(data.shape)

    save_anchors={}
    for i in range(len(data)):
            spatialcell_cluid=d_spatial[data[i,0]]
            singlecell_cluid=d_single[data[i,1]]
            #print(i,spatialcell_cluid,singlecell_cluid)
            col=d_spatial_cluster[spatialcell_cluid]
            row=d_single_cluster[singlecell_cluid]
            mat21[row,col]+=1
            mat22[col,row]+=1
            key=str(col)+'#'+str(row)
            name=data[i,0]+'#'+data[i,1]
            if key not in save_anchors:
                save_anchors[key]=[name]
            else:
                if name not in save_anchors[key]:
                    save_anchors[key].append(name)

    #col normalization
    for i in range(len(mat21[0])):
        mat21[:,i]=mat21[:,i]/np.sum(mat21[:,i])

    for i in range(len(mat22[0])):
        mat22[:,i]=mat22[:,i]/np.sum(mat22[:,i])


    #print(mat2.shape,anchorFreqRow.shape,anchorFreqCol.shape,len(input.lsc[0]),len(input.lsp[0]),input.MNN_across_spatial_clusters_dispersion_cutoff)
    newmat2=np.vstack((anchorFreqCol,mat22))
    mat2=np.vstack((anchorFreqRow,mat21))
    cname2=input.lsp[0]
    newcname2=input.lsc[0]

    #sometimes guided spatial clusters anchors to
    #few cells so need to find out those clusters
    #and they should never be removed from the dispersion cutoff parameters
    fw=open(input.savepath+"spatial_annotation_along_SP.dat",'w')
    unique_rep_of_leiden_clusters_in_sp={}
    for i in range(mat2.shape[1]):
        af=mat2[0,i]
        col=mat2[1:,i]
        index=np.argsort(-col)
        found=''
        for j in range(len(col)):
            value=col[index[j]]
            nct=input.lsc[0][index[j]]
            if value>input.MNN_across_spatial_clusters_dispersion_cutoff:
                if j!=0:
                    found+=', '
                found+=nct+':'+'%0.3f'%value
                if cname2[i] not in unique_rep_of_leiden_clusters_in_sp:
                    unique_rep_of_leiden_clusters_in_sp[cname2[i]]=[nct]
                else:
                    if nct not in unique_rep_of_leiden_clusters_in_sp[cname2[i]]:
                        unique_rep_of_leiden_clusters_in_sp[cname2[i]].append(nct)
        fw.write(str(i)+'\t'+cname2[i]+'\tF='+str('%0.3f'%af)+',\t'+found+'\n')

    #these clusters should not be removed
    low_anchors_spatial_clusters={}
    for key in unique_rep_of_leiden_clusters_in_sp:
        temp=unique_rep_of_leiden_clusters_in_sp[key]
        if len(temp)==1:
            low_anc_ct=temp[0]
            if low_anc_ct not in low_anchors_spatial_clusters:
                low_anchors_spatial_clusters[low_anc_ct]=[key]
            else:
                low_anchors_spatial_clusters[low_anc_ct].append(key)

    print(low_anchors_spatial_clusters)
    #{'KCs': ['c11', 'c7'], 'Stellatecells': ['c12'], 'Cholangiocytes': ['c16'], 'Bcells': ['c17'], 'LSECs': ['c18', 'c6']}


    fw.close()
    fw=open(input.savepath+"spatial_annotation_along_SC.dat",'w')
    good_anchors={}
    tt=[]
    for i in range(newmat2.shape[1]):
        af=newmat2[0,i]
        col=newmat2[1:,i]
        index=np.argsort(-col)
        found=''
        for j in range(len(col)):
            flag=0
            if col[index[j]]>input.MNN_across_spatial_clusters_dispersion_cutoff:
                flag=1
                # this flag is true if spillovered anchores belong to other leiden cluster are > dispersion cutoff
            elif newcname2[i] in low_anchors_spatial_clusters:
                if input.lsp[0][index[j]] in low_anchors_spatial_clusters[newcname2[i]]:
                    flag=0
                # this flag is true if spillovered anchores belong to other leiden cluster < dispersion but uniquly mapped

            if flag==1:
                if j!=0:
                    found+=', '
                found+=input.lsp[0][index[j]]+':'+'%0.3f'%col[index[j]]

                key=str(index[j])+'#'+str(i)
                tt.append(key)
                if key in save_anchors:
                    list_of_anchors=save_anchors[key]
                    for k in range(len(list_of_anchors)):
                        name=list_of_anchors[k]
                        #print(name)
                        if name not in good_anchors:
                            good_anchors[name]=1
                        else:
                            good_anchors[name]+=1

        fw.write(str(i)+'\t'+newcname2[i]+'\tF='+str('%0.3f'%af)+',\t'+found+'\n')
    fw.close()


    print(len(np.unique(tt)))
    print(len(np.unique(list(save_anchors.keys()))))

    c=0
    for key in good_anchors:
        c+=good_anchors[key]

    count=0
    ca={}
    for key in save_anchors:
        list_of_anchors=save_anchors[key]
        count+=len(list_of_anchors)
        for j in range(len(list_of_anchors)):
            ca[list_of_anchors[j]]=1

    print('good anchors',len(good_anchors),c,'\t\tsave',len(ca),count)





    colname=['total # of sc', 'total # of sp']
    cname1=['anchorFreq']+list(input.lsc[0])





    #print(cname2)
    #fig,ax=plt.subplots(1,2,figsize=(20,10))
    fig=plt.figure(figsize=(15,10))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 10])
    ax0=plt.subplot(gs[0])
    ax1=plt.subplot(gs[1])
    fig.suptitle('MNN K = ' + str(input.KNN),fontsize=12)
    #snn.heatmap(ax=ax0,data=mat1,annot=True, fmt='d',xticklabels=colname, annot_kws={"size": 5},yticklabels=cname1)

    snn.heatmap(ax=ax1,data=mat2,annot=True, fmt='0.2f',xticklabels=cname2, annot_kws={"size": 5},yticklabels=cname1)
    plt.xlabel('Spatial cell clusters')
    plt.ylabel('Single cell clusters')

    #plt.title('R = '+str(radius)+', C='+str(lambda_c))
    #g.xaxis.set_ticks_position("top")
    plt.tight_layout()
    fig.savefig(input.savepath+'Res_MNN_K_'+str(input.KNN)+'.png',dpi=300)

    return good_anchors




def built_MNN_matrix_between_sc_and_sp(input):
#def main():
    '''
    scdatapath='./inputSC/'
    spdatapath='./inputSP/'
    outputFolder=spdatapath+'find_MNN/'
    neigh=50
    no_of_pc=50
    '''

    spatial_deg_annotation_output_clustername=input.spatial_annotation_output_fname+'_cluster.csv'
    spatial_deg_annotation_output_celltypename=input.spatial_annotation_output_fname+'_ct_name.dat'
    outputFolder=input.outputFolder
    neigh=input.neigh
    no_of_pc=input.no_of_pc
    MNN_across_spatial_clusters_dispersion_cutoff=input.MNN_across_spatial_clusters_dispersion_cutoff
    resolutionWiseClustering=input.resolutionWiseClustering
    minkowski_order=input.minkowski_order
    number_of_iteration_in_degree_based_annotations=input.number_of_iteration_in_degree_based_annotations

    create_directory(outputFolder)

    #method='gauss'
    method='umap'

    annotation_spatial_barcode_id= input.sp_cluster[:,0]
    annotation_spatial_cluster_id= input.sp_cluster[:,1]
    #print(np.unique(annotation_spatial_cluster_id))
    spatialcell_unique_clustername=input.sp_ct_name[:,1]
    spatialcell_unique_clusterid=input.sp_ct_name[:,0]
    d={}
    for i in range(len(input.sp_ct_name)):
        #print(i,input.sp_ct_name[i,0],type(input.sp_ct_name[i,0]),input.sp_ct_name[i,1])
        d[input.sp_ct_name[i,0]]=input.sp_ct_name[i,1]
    annotation_spatial_celltypename=[]
    for i in range(len(annotation_spatial_cluster_id)):
        #print(i,annotation_spatial_cluster_id[i],type(annotation_spatial_cluster_id[i]))
        annotation_spatial_celltypename.append(d[annotation_spatial_cluster_id[i]])
    annotation_spatial_celltypename=np.array(annotation_spatial_celltypename)



    annotation_singlecell_barcode_id=input.sc_cluster[:,0]
    annotation_singlecell_cluster_id=input.sc_cluster[:,1]
    singlecell_unique_clustername=input.sc_ct_name[:,1]
    singlecell_unique_clusterid=input.sc_ct_name[:,0]
    d={}
    for i in range(len(input.sc_ct_name)):
        d[input.sc_ct_name[i,0]]=input.sc_ct_name[i,1]
    annotation_singlecell_celltypename=[]
    for i in range(len(annotation_singlecell_cluster_id)):
        annotation_singlecell_celltypename.append(d[annotation_singlecell_cluster_id[i]])
    annotation_singlecell_celltypename=np.array(annotation_singlecell_celltypename)


    '''
    singlecell_unique_clustername=sorted(list(np.unique(annotation_singlecell_celltypename)))
    d={}
    singlecell_unique_clusterid=[]
    for i in range(len(singlecell_unique_clustername)):
        d[singlecell_unique_clustername[i]]=i
        singlecell_unique_clusterid.append(i)
    annotation_singlecell_cluster_id=[]
    for i in range(len(annotation_singlecell_celltypename)):
        annotation_singlecell_cluster_id.append(d[annotation_singlecell_celltypename[i]])
    annotation_singlecell_cluster_id=np.array(annotation_singlecell_cluster_id)
    '''

    #fmnn=outputFolder+"sct_pairing_gene_expression_space.csv"
    fmnn=outputFolder+"sct_pairing_shared_common_gene_PC_"+str(neigh)+".csv"
    #fmnn="./common_MNN/sct_pairing_shared_common_gene_PC_common.csv"

    #fmnn=outputFolder+"sct_pairing_shared_common_gene_PC.csv"

    fname=outputFolder+'/KnearestNeighbors'+str(neigh)+'.dat'
    fdist=outputFolder+'/KnearestDist'+str(neigh)+'.dat'


    flag=1
    if os.path.isfile(fmnn):
        filesize = os.path.getsize(fmnn)
        if filesize>0:
            flag=0

    if flag==1:
        '''
        ad_sc_ori=sc.read_h5ad(datapath+'sc_liver_data.h5ad')
        ad_sc_ori.var_names_make_unique()

        ad_sp_ori=sc.read_h5ad(datapath+'spatial_quadrant.h5ad')
        sc.pp.filter_cells(ad_sp_ori, min_counts=2)
        ad_sp_ori.var_names_make_unique()

        sp_genename=ad_sp_ori.var_names.to_numpy()
        sc_genename=ad_sc_ori.var_names.to_numpy()
        index_sp,index_sc=find_index(sp_genename,sc_genename)

        print('before sct normalization of single cell',len(index_sp),len(index_sc))
        ad_sc=ad_sc_ori[:,index_sc].copy()
        ad_sp=ad_sp_ori[:,index_sp].copy()
        '''

        if os.path.isfile(input.spfname):
            filesize = os.path.getsize(input.spfname)
            if filesize>0:
                sct_ad_sp=sc.read_h5ad(input.spfname)
        else:
            print("your input is wrong")
            sct_ad_sp = SCTransform(ad_sp,min_cells=5,gmean_eps=1,n_genes=500,n_cells=None, #use all cells
                        bin_size=500,bw_adjust=3,inplace=False)
            sct_ad_sp.write_h5ad(fname)

        #fname=scdatapath+'scTransform_singleCell_si.h5ad'
        if os.path.isfile(input.scfname):
            filesize = os.path.getsize(input.scfname)
            if filesize>0:
                sct_ad_sc=sc.read_h5ad(input.scfname)
        else:
            print("your input is wrong")
            sct_ad_sc = SCTransform(ad_sc,min_cells=5,gmean_eps=1,n_genes=500,n_cells=None, #use all cells
                        bin_size=500,bw_adjust=3,inplace=False)
            sct_ad_sc.write_h5ad(fname)



        sp_genename=sct_ad_sp.var_names.to_numpy()
        sc_genename=sct_ad_sc.var_names.to_numpy()
        index_sp,index_sc=find_index(sp_genename,sc_genename)
        print('after sct normalization of single cell',len(index_sp),len(index_sc))

        ad_sp_ori=sct_ad_sp[:,index_sp].copy()
        ad_sc_ori=sct_ad_sc[:,index_sc].copy()

        ad_sc_ori.write_h5ad(outputFolder+'final_sct_sc.h5ad')
        ad_sp_ori.write_h5ad(outputFolder+'final_sct_sp.h5ad')

        print('\n\n 3 sct Shared Common Gene PC space')
        #ad_sp_ori=ad_sp_ori[0:100,:]
        #ad_sc_ori=ad_sc_ori[0:100,:]
        #print(ad_sc_ori)
        #print(ad_sp_ori)
        input_sp,input_sc,sp_barcode,sc_barcode=sct_return_sc_sp_in_shared_common_PC_space(ad_sp_ori,ad_sc_ori,no_of_pc,method)
        print('sp',input_sp.shape,'\nsc',input_sc.shape)


        if os.path.isfile(fname):
            pass
        else:
            n_jobs=-1
            #input_sp=input_sp[0:20]
            print(input_sp.shape)
            k_dist,k_index = cKDTree(input_sp).query(x=input_sp, k=neigh, p=minkowski_order,workers=n_jobs)
            fw=open(fname,'w')
            for i in range(len(k_index)):
                for j in range(len(k_index[i])):
                    id=k_index[i,j]
                    fw.write(sp_barcode[id]+',')
                fw.write('\n')
            fw.close()
            pd.DataFrame(k_dist).to_csv(fdist,float_format='%.3f',index=False,header=None)

        corrected = find_mutual_nn(minkowski_order,input_sp,input_sc,sp_barcode,sc_barcode, k1= neigh,k2= neigh)
        pd.DataFrame(corrected).to_csv(fmnn,index=False,header=None)



    if flag==0:
        ad_sc_ori=sc.read_h5ad(outputFolder+'final_sct_sc.h5ad')
        ad_sp_ori=sc.read_h5ad(outputFolder+'final_sct_sp.h5ad')
        singlecell_sct_barcode_id=ad_sc_ori.obs_names.to_numpy()
        spatialcell_sct_barcode_id=ad_sp_ori.obs_names.to_numpy()
        input={}
        #fmnn="./common_MNN/sct_pairing_shared_common_gene_PC_common.csv"
        #fname=''
        input['fname']=fmnn
        input['annotation_singlecell_barcode_id']=annotation_singlecell_barcode_id
        input['annotation_singlecell_celltypename']=annotation_singlecell_celltypename
        input['annotation_singlecell_cluster_id']=annotation_singlecell_cluster_id
        input['lsc']=[singlecell_unique_clustername,singlecell_unique_clusterid]
        input['sct_singlecell_barcode_id']=singlecell_sct_barcode_id
        input['sct_spatial_barcode_id']=spatialcell_sct_barcode_id
        input['annotation_spatial_barcode_id']=annotation_spatial_barcode_id
        input['annotation_spatial_celltypename']=annotation_spatial_celltypename
        input['annotation_spatial_cluster_id']=annotation_spatial_cluster_id
        input['lsp']=[spatialcell_unique_clustername, spatialcell_unique_clusterid]
        input['savepath']=outputFolder
        input['KNN']=neigh
        input['KNNfilename']=fname
        input['ad_sp']=ad_sp_ori
        input['spatial_deg_annotation_output_clustername']=spatial_deg_annotation_output_clustername
        input['spatial_deg_annotation_output_celltypename']=spatial_deg_annotation_output_celltypename
        input['MNN_across_spatial_clusters_dispersion_cutoff']=MNN_across_spatial_clusters_dispersion_cutoff
        input['resolutionWiseClustering']=resolutionWiseClustering
        input['number_of_iteration_in_degree_based_annotations']=number_of_iteration_in_degree_based_annotations


        inputt=SimpleNamespace(**input)
        good_anchors=find_commnon_MNN(inputt)
        degree_based_annotation(inputt,good_anchors)

    return 0

#main()

def degree_based_annotation(input,good_anchors):
    chosenKNN=input.KNN

    resolutionClusterWise=[]
    for k in range(len(input.resolutionWiseClustering)):
        sp_leiden_barcode2cluid={}
        sp_leiden_cluid2barcode={}
        resolutionwise_spatial_barcode_id=input.resolutionWiseClustering[k]
        #print('ankit',resolutionwise_spatial_barcode_id[0:5])
        for i in range(len(resolutionwise_spatial_barcode_id)):
            id=resolutionwise_spatial_barcode_id[i,1]
            name=resolutionwise_spatial_barcode_id[i,0]
            sp_leiden_barcode2cluid[name]=id
            '''
            if id not in sp_leiden_cluid2barcode:
                sp_leiden_cluid2barcode[id]=[name]
            else:
                sp_leiden_cluid2barcode[id].append(name)
            '''
        resolutionClusterWise.append(sp_leiden_barcode2cluid)


    deg,G=read_KNN_file(input.KNNfilename)

    df=pd.read_csv(input.fname,header=None)
    mnn=df.to_numpy()

    print("all mnn",mnn.shape)

    index=[]
    for i in range(len(mnn)):
        name=mnn[i,0]+'#'+mnn[i,1]
        if name in good_anchors:
            index.append(i)
    mnn=mnn[index,:]

    print("good mnn",mnn.shape)

    sc_ctype_id=input.lsc[1]
    sc_ctype_name=input.lsc[0]


    a=np.reshape(input.annotation_singlecell_barcode_id,(len(input.annotation_singlecell_barcode_id),1))
    b=np.reshape(input.annotation_singlecell_cluster_id,(len(input.annotation_singlecell_cluster_id),1))

    sc_clusters=np.hstack((a,b))


    sp_cell_identity=find_all_the_spatial_cells_mapped_to_single_cells(sc_ctype_id,sc_clusters,mnn,sc_ctype_name)


    #fw=open('spatial_cell_identity'+str(chosenKNN)+'.dat','w')
    unique_mapped={}
    confused={}
    all_mapped={}
    for key in sp_cell_identity:
        name=''
        a=sp_cell_identity[key]
        #print('1' , a)
        for j in range(len(a)):
            name+='_a#d_'+a[j][0]
        if len(a)==1:
            unique_mapped[key]=a[0][0]
        else:
            t1=[]
            t2=[]
            for j in range(len(a)):
                t1.append(a[j][1])
                t2.append(a[j][0])
            confused[key]=t2
            #print(key,t1,t2)
        all_mapped[key]=name[5:]
        #fw.write(key+'\t'+str(name)+'\n')


    print('unique mapped 1',len(unique_mapped))
    fw=open(input.savepath+'unique_mapped.dat','w')
    for key in unique_mapped:
        fw.write(key+'\t'+'0\n')
    fw.close()

    ad_sp= input.ad_sp
    cellname=ad_sp.obs_names.to_numpy()
    genename=ad_sp.var_names.to_numpy()
    #print(cellname[0:5],genename[0:5])


    saveunique_mapped=unique_mapped

    for res in range(len(resolutionClusterWise)):
        unique_mapped=saveunique_mapped
        all_anchored_mapped=resolved_confused_and_unmapped_mapping_of_cells_deg(confused,G,all_mapped,unique_mapped,[resolutionClusterWise[res]])
        print('unique mapped 2',len(all_anchored_mapped))
        availabled_anchors_mapped=all_anchored_mapped

        for iter in range(input.number_of_iteration_in_degree_based_annotations):
            unmapped_cellname,unmapped_deg=find_unmapped_cells_and_deg(deg,availabled_anchors_mapped)
            unique_mapped=resolved_confused_and_unmapped_mapping_of_cells_deg(unmapped_cellname,G,availabled_anchors_mapped,availabled_anchors_mapped,[resolutionClusterWise[res]])
            print('iter',iter,len(unique_mapped),len(unmapped_cellname),len(unmapped_deg))


            for i in range(len(cellname)):
                key=cellname[i]
                if key not in unique_mapped:
                    unique_mapped[key]='NotMapped'

            count=0
            availabled_anchors_mapped={}
            for key in unique_mapped:
                if unique_mapped[key]=='NM':
                    count+=1
                else:
                    availabled_anchors_mapped[key]=unique_mapped[key]
            #print('Iter',iter,count)


            deg_annot_cluster_fname=input.savepath+str(iter+1)+'_'+input.spatial_deg_annotation_output_clustername
            deg_annot_ct_fname=input.savepath+str(iter+1)+'_'+input.spatial_deg_annotation_output_celltypename

            write_annotation(deg_annot_cluster_fname,deg_annot_ct_fname,unique_mapped,cellname)



def read_KNN_file(KNNfilename):
    f=open(KNNfilename)
    neighbors=[]
    for line in f:
        l=line[0:-1].split(',')
        neighbors.append(l[0:-1])
    edges=[]
    all_edges=[]
    d={}
    for j in range(len(neighbors)):
    #for j in range(1):
        l=neighbors[j]
        #for m in range(len(l)):
        for n in range(1,len(l)):
            temp=sorted([l[0],l[n]])
            name=temp[0]+'#'+temp[1]
            d[name]=1

            #all_edges.append([l[0].replace('cell',''),l[n].replace('cell','')])
    for key in d:
        name=key.split('#')
        #print(key,name)
        all_edges.append(name)


    G=nx.Graph()
    G.add_edges_from(all_edges)
    deg = [d for (v, d) in G.degree()]
    nodes = [v for (v, d) in G.degree()]

    deg={}
    for (n,d) in G.degree:
        deg[n]=d

    return deg,G


def return_singlecells(cluster_data,midzone):
    barcode_id= cluster_data[:,0]
    cluster_id= cluster_data[:,1]
    index=np.where(cluster_id==midzone)
    midzoneCells=barcode_id[index[0]]
    return np.unique(midzoneCells)



def findSpatialCells(midzoneCells,mnn):
    d={}
    for i in range(len(midzoneCells)):
        first=midzoneCells[i]
        index=np.where(mnn[:,1]==first)
        spcells=mnn[index[0],0]
        #print(spcells)
        for k in range(len(spcells)):
            if spcells[k] not in d:
                d[spcells[k]]=1
            else:
                d[spcells[k]]+=1
    return d


def find_all_the_spatial_cells_mapped_to_single_cells(sc_ctype_id,sc_clusters,mnn,sc_ctype_name):
    spdata=[]
    # single cell cluster id sc_ctype_id
    # single cell cluster name sc_ctype_name
    for i in range(len(sc_ctype_id)):
        sc_ct_specific_cells=return_singlecells(sc_clusters,sc_ctype_id[i])
        # all the single cell barcode id of sc_ctype_name[i]
        sp_ct_specific_cells=findSpatialCells(sc_ct_specific_cells,mnn)
        #print('1',i,sc_ctype_id[i],len(sp_ct_specific_cells))
        spdata.append(sp_ct_specific_cells)
        #print(sc_ctype_name[i], '\tSC',len(sc_ct_specific_cells),'\tSP',len(sp_ct_specific_cells))

    sp_cell_identity={}
    for i in range(len(sc_ctype_id)):
        a=spdata[i] # this is dictionary
        for name in a:
            if name not in sp_cell_identity:
                sp_cell_identity[name]=[[sc_ctype_name[i],a[name]]]
            else:
                sp_cell_identity[name].append([sc_ctype_name[i],a[name]])

    for key in sp_cell_identity:
        a=sp_cell_identity[key]
        #print(a)
        if len(a)>1:
            #print(key, a)
            t1=[]
            t2=[]
            for j in range(len(a)):
                t1.append(a[j][1])
                t2.append(a[j][0])
            ind=np.argsort(-np.array(t1))
            if t1[ind[0]]>t1[ind[1]]:
                b=[[t2[ind[0]],t1[ind[0]]]]
                sp_cell_identity[key]=b

        '''
        a=list(spdata[i])
        for j in range(len(a)):
            name=a[j]
            if name not in sp_cell_identity:
                sp_cell_identity[name]=[sc_ctype_name[i]]
            else:
                sp_cell_identity[name].append(sc_ctype_name[i])
        '''

    return sp_cell_identity

def write_annotation(deg_annot_cluster_fname,deg_annot_ct_fname,unique_mapped,cellname):
    sc_ctype_name=[]
    d2={}
    for key in unique_mapped:
        a=unique_mapped[key]
        if a not in d2:
            d2[a]=1
        else:
            d2[a]+=1
        if a not in sc_ctype_name:
            sc_ctype_name.append(a)

    #print(sc_ctype_name)
    #print(d.keys())
    sc_ctype_name=sorted(sc_ctype_name)
    fw=open(deg_annot_ct_fname,'w')
    d={}
    for i in range(len(sc_ctype_name)):
        fw.write(str(i)+','+sc_ctype_name[i]+','+str(d2[sc_ctype_name[i]])+'\n')
        d[sc_ctype_name[i]]=i
    fw.close()

    #keys=sorted(list(unique_mapped.keys()))
    fw=open(deg_annot_cluster_fname,'w')
    fw.write('barcode,mnn_based_annot\n')
    for i in range(len(cellname)):
        barcodeid=cellname[i]
        ctname=unique_mapped[barcodeid]
        fw.write(barcodeid+','+str(d[ctname])+'\n')
    fw.close()



def find_unmapped_cells_and_deg(deg,unique_mapped):
    un_mapped_nodes=[]
    un_mapped_deg=[]
    for node in deg:
        if node not in unique_mapped:
            un_mapped_nodes.append(node)
            un_mapped_deg.append(deg[node])

    un_mapped_deg=np.array(un_mapped_deg)
    un_mapped_nodes=np.array(un_mapped_nodes)
    index=np.argsort(-un_mapped_deg)

    cellname=un_mapped_nodes[index]
    degvalue=un_mapped_deg[index]

    return cellname,degvalue


def resolved_confused_and_unmapped_mapping_of_cells_distance(confused,G,all_mapped):
    for mainkey in confused:
            a=G[mainkey]
            t=[]
            t1=[]
            for key in a:
                if key in all_mapped:
                    t.append(a[key]['weight'])
                    t1.append(key)
            t=np.array(t)
            t1=np.array(t1)
            ind=np.argsort(t)
            #print('4',len(t),t[ind])

            if len(t)>0:
                key=t1[ind[0]]
                t=[all_mapped[key]]
                t1=[]
                t2=[]
                t3=[]
                t4=[]
                for i in range(len(t)):
                    t1.append(t[i][2])
                    t2.append(t[i][0])
                    t3.append(t[i][1])
                    t4.append(t[i][3])
                ind=np.argsort(np.array(t1))
                finalone=[t2[ind[0]], t3[ind[0]],    t1[ind[0]] , t4[ind[0]]      ]
            else:
                finalone=['NM', -1,  99999999, 'Null'  ]
            #print('6',finalone1)

            all_mapped[mainkey]=finalone

    return all_mapped

def resolved_confused_and_unmapped_mapping_of_cells_deg(confused,G,all_mapped,unique_mapped,sp_leiden_barcode2cluid_resolution_wise):

    for mainkey in confused:
            #for i in range(len(neighbor)):
            a=G[mainkey]
            current_clu_id=[]
            x=[]
            for res in range(len(sp_leiden_barcode2cluid_resolution_wise)):
                sp_leiden_barcode2cluid=sp_leiden_barcode2cluid_resolution_wise[res]
                current_clu_id.append(sp_leiden_barcode2cluid[mainkey])
                x.append([])

            t=[]
            for key in a:
                if key in all_mapped:
                    t.append(all_mapped[key])
                    for res in range(len(sp_leiden_barcode2cluid_resolution_wise)):
                        sp_leiden_barcode2cluid=sp_leiden_barcode2cluid_resolution_wise[res]
                        if current_clu_id[res]==sp_leiden_barcode2cluid[key]:
                            #x.append(str(sp_leiden_barcode2cluid[key])+'#'+all_mapped[key])
                            x[res].append(all_mapped[key])


            if True:
                neigh_clu_id=[]
                for res in range(len(sp_leiden_barcode2cluid_resolution_wise)):
                    neigh_clu_id.append(list(np.unique(x[res]))) #     Counter(x)
                c=Counter(t)
                totalsum=sum(c.values())
                #print('a',mainkey,c,totalsum)#,confused[mainkey])
                #print('b',current_clu_id,neigh_clu_id)
                low2high=sorted(c, key=c.get)
                high2low=low2high[::-1]
                #print(high2low,c)
                t2=[]
                t1=[]
                for i in range(len(high2low)):
                    if high2low[i].find('_a#d_')==-1:
                        t1.append(c[high2low[i]])
                        t2.append(high2low[i])
                t1=np.array(t1)
                index=np.argsort(-t1)
                #print('index',index,t1[index])

                finalone='NM'
                for i in range(len(t1)):
                    localdeg=t1[index[i]]
                    localctname=t2[index[i]]
                    #print(localdeg,localctname)

                    temp=[]
                    for res in range(len(neigh_clu_id)):
                        if localctname in neigh_clu_id[res]:
                            temp.append(localctname)

                    if len(np.unique(temp))==1:
                        finalone=temp[0]
                        break

                #print(len(t1),t1,t2,)#,t3,expected)
                #print('cc',current_clu_id,neigh_clu_id)
                if len(t1)==0:
                    finalone='NM'
                else:
                    finalone=finalone#t2[index]

                #print('final',finalone)
                #print('\n\n')
                unique_mapped[mainkey]=finalone


    return unique_mapped

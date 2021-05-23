from kubernetes import client as k8s_client
from kubernetes import client, config
import time
import pandas as pd

dict_ = {'name_of_deployment':[],
	'image_of_deployment':{'image_name':[],'status':[]},
	'date_deployment_updated':{'name':[],'latest_update_time':[]}
	}

config.load_kube_config()
def main():

	resp = client.AppsV1Api()
	V1=client.CoreV1Api()
	deployed = resp.list_namespaced_deployment(namespace="sock-shop")
	ret = V1.list_namespaced_pod(namespace="sock-shop")
	

	for i in deployed.items:
		dict_['name_of_deployment'].append(i.metadata.name)

	df_deployment_name = pd.DataFrame(dict_['name_of_deployment'], columns=['Name of deployment'])
	
	for V2 in ret.items:
		if V2.status.pod_ip == None:
			dict_['image_of_deployment']['status'].append('Pending')
		else:
			dict_['image_of_deployment']['status'].append('Running')
			 
		dict_['image_of_deployment']['image_name'].append(V2.metadata.name)
    		
	df_image_deployment = pd.DataFrame(dict_['image_of_deployment'])
	
	
	frames = []
	for name in df_deployment_name['Name of deployment'].values:
		flag = 0
		row_df = pd.DataFrame()
		results = [image for image in df_image_deployment['image_name'].values if name in image]
		if 'db' in name:
			flag = 1
		if flag:
			found = [r for r in results if 'db' in r]
		else:
			found = [r for r in results if 'db' not in r]
		
		for f in found:
			row_df = pd.DataFrame(df_image_deployment.loc[df_image_deployment['image_name'] == f])
			row_df['deployment_name'] = name
			frames.append(row_df)

	concat_df = pd.concat(frames)
	
	
	for i in deployed.items:
		conditions = i.status.conditions
		for j in range(len(conditions)):
			dict_['date_deployment_updated']['latest_update_time'].append(conditions[j].last_update_time)
			dict_['date_deployment_updated']['name'].append(i.metadata.name)
	df_depolyed_df = pd.DataFrame(dict_['date_deployment_updated'])
	
	
	new_frame = []
	for idx in range(len(df_depolyed_df['name'].values)):
		row_df = pd.DataFrame(concat_df.loc[concat_df['deployment_name'] == df_depolyed_df.iloc[idx]['name']])
		row_df['date_deployment_updated'] = df_depolyed_df.iloc[idx]['latest_update_time']
		new_frame.append(row_df)
	print(pd.concat(new_frame))
main()

source ./deploy_eks/config.sh

# DOMAIN=kubectl -n $NAME get svc $NAME -o wide | awk 'FNR==2{print $4}'
kubectl get -n $NAME svc $NAME -o wide | awk 'FNR==2{split($5,a,":"); if(a[1]=="80") print "http://"$4; else if(a[1]=="443") print "https://"$4}'

# PORT=kubectl -n {name-your-service} get svc {name-your-service} -o wide | awk 'FNR==2{print $5}' | cut -d: -f1
# curl http://a5554240a8ade41e1b7e5b1261f17556-36a1218235723fef.elb.us-east-1.amazonaws.com
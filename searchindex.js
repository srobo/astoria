Search.setIndex({docnames:["design/code_format","design/history","design/index","design/ipc","design/metadata","design/requirements","development/index","implementation/consumers/astctl","implementation/consumers/index","implementation/data_components","implementation/index","implementation/managers/astdiskd","implementation/managers/astmetad","implementation/managers/astprocd","implementation/managers/index","index","usage"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":3,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":2,"sphinx.domains.rst":2,"sphinx.domains.std":1,"sphinx.ext.intersphinx":1,"sphinx.ext.viewcode":1,sphinx:56},filenames:["design/code_format.rst","design/history.rst","design/index.rst","design/ipc.rst","design/metadata.rst","design/requirements.rst","development/index.rst","implementation/consumers/astctl.rst","implementation/consumers/index.rst","implementation/data_components.rst","implementation/index.rst","implementation/managers/astdiskd.rst","implementation/managers/astmetad.rst","implementation/managers/astprocd.rst","implementation/managers/index.rst","index.rst","usage.rst"],objects:{"astoria.common.disk_constraints":{AndConstraint:[11,0,1,""],Constraint:[11,0,1,""],FalseConstraint:[11,0,1,""],FilePresentConstraint:[11,0,1,""],NotConstraint:[11,0,1,""],NumberOfFilesConstraint:[11,0,1,""],OrConstraint:[11,0,1,""],TrueConstraint:[11,0,1,""]},"astoria.common.disk_constraints.AndConstraint":{__init__:[11,1,1,""],matches:[11,1,1,""]},"astoria.common.disk_constraints.Constraint":{matches:[11,1,1,""]},"astoria.common.disk_constraints.FalseConstraint":{matches:[11,1,1,""]},"astoria.common.disk_constraints.FilePresentConstraint":{__init__:[11,1,1,""],matches:[11,1,1,""]},"astoria.common.disk_constraints.NotConstraint":{__init__:[11,1,1,""],matches:[11,1,1,""]},"astoria.common.disk_constraints.NumberOfFilesConstraint":{__init__:[11,1,1,""],matches:[11,1,1,""]},"astoria.common.disk_constraints.OrConstraint":{__init__:[11,1,1,""],matches:[11,1,1,""]},"astoria.common.disk_constraints.TrueConstraint":{matches:[11,1,1,""]},"astoria.common.manager_requests":{ManagerRequest:[3,0,1,""],RequestResponse:[3,0,1,""]},"astoria.common.manager_requests.ManagerRequest":{sender_name:[3,2,1,""],uuid:[3,2,1,""]},"astoria.common.manager_requests.RequestResponse":{reason:[3,2,1,""],success:[3,2,1,""],uuid:[3,2,1,""]},"astoria.common.messages.astdiskd":{DiskInfo:[11,0,1,""],DiskManagerMessage:[11,0,1,""],DiskType:[11,0,1,""],DiskUUID:[11,0,1,""]},"astoria.common.messages.astdiskd.DiskInfo":{disk_type:[11,2,1,""],mount_path:[11,2,1,""],uuid:[11,2,1,""]},"astoria.common.messages.astdiskd.DiskManagerMessage":{disks:[11,2,1,""]},"astoria.common.messages.astdiskd.DiskType":{METADATA:[11,2,1,""],NOACTION:[11,2,1,""],UPDATE:[11,2,1,""],USERCODE:[11,2,1,""],determine_disk_type:[11,1,1,""]},"astoria.common.messages.astmetad":{Metadata:[12,0,1,""],MetadataManagerMessage:[12,0,1,""],RobotMode:[12,0,1,""]},"astoria.common.messages.astmetad.Metadata":{Config:[12,0,1,""],arch:[12,2,1,""],arena:[12,2,1,""],astoria_version:[12,2,1,""],game_timeout:[12,2,1,""],init:[12,1,1,""],kernel_version:[12,2,1,""],kit_name:[12,2,1,""],kit_version:[12,2,1,""],libc_ver:[12,2,1,""],mode:[12,2,1,""],python_version:[12,2,1,""],wifi_enabled:[12,2,1,""],wifi_password:[12,2,1,""],wifi_ssid:[12,2,1,""],zone:[12,2,1,""]},"astoria.common.messages.astmetad.Metadata.Config":{validate_assignment:[12,2,1,""]},"astoria.common.messages.astmetad.MetadataManagerMessage":{metadata:[12,2,1,""]},"astoria.common.messages.astmetad.RobotMode":{COMP:[12,2,1,""],DEV:[12,2,1,""]},"astoria.common.messages.astprocd":{CodeStatus:[13,0,1,""],ProcessManagerMessage:[13,0,1,""]},"astoria.common.messages.astprocd.CodeStatus":{CRASHED:[13,2,1,""],FINISHED:[13,2,1,""],KILLED:[13,2,1,""],RUNNING:[13,2,1,""],STARTING:[13,2,1,""]},"astoria.common.messages.astprocd.ProcessManagerMessage":{code_status:[13,2,1,""],disk_info:[13,2,1,""]},"astoria.managers.astdiskd":{DiskManager:[11,0,1,""]},"astoria.managers.astdiskd.DiskManager":{main:[11,1,1,""],name:[11,2,1,""],offline_status:[11,1,1,""],update_state:[11,1,1,""]},"astoria.managers.astmetad":{MetadataManager:[12,0,1,""]},"astoria.managers.astmetad.MetadataManager":{dependencies:[12,2,1,""],get_current_metadata:[12,1,1,""],handle_disk_insertion:[12,1,1,""],handle_disk_removal:[12,1,1,""],handle_mutation_request:[12,1,1,""],main:[12,1,1,""],name:[12,2,1,""],offline_status:[12,1,1,""],update_status:[12,1,1,""]},"astoria.managers.astprocd":{ProcessManager:[13,0,1,""]},"astoria.managers.astprocd.ProcessManager":{dependencies:[13,2,1,""],handle_disk_insertion:[13,1,1,""],handle_disk_removal:[13,1,1,""],handle_kill_request:[13,1,1,""],handle_restart_request:[13,1,1,""],main:[13,1,1,""],name:[13,2,1,""],offline_status:[13,1,1,""],update_status:[13,1,1,""]}},objnames:{"0":["py","class","Python class"],"1":["py","method","Python method"],"2":["py","attribute","Python attribute"]},objtypes:{"0":"py:class","1":"py:method","2":"py:attribute"},terms:{"0dev":[0,16],"120":16,"1883":16,"2021":0,"2022":[0,15],"2dev":0,"534912":0,"53491266d26fcb504eb4b1d9108de04899832c83":0,"abstract":11,"break":0,"case":13,"class":[3,14],"default":[11,12,16],"function":[8,9],"import":14,"int":[11,12],"long":[0,16],"new":13,"public":[0,3,6],"return":[11,12,13,14],"short":0,"static":12,"true":[11,12,14,16],For:[4,7,15,16],IDE:6,Not:[1,11],OSes:16,The:[0,3,4,5,6,9,11,13,15,16],There:[3,12,16],These:5,Use:5,Used:3,Useful:11,Uses:1,__init__:11,__main__:14,__name__:14,_init:14,_post_connect:9,_post_disconnect:9,_pre_connect:9,_pre_disconnect:9,abc:0,abil:5,abl:4,about:[3,11,16],abov:[5,13],access:6,accident:6,action:3,added:12,addit:[3,12,13],after:[3,9,11],against:11,aim:5,alert:3,all:[1,3,4,6,16],allow:[3,5,11,14],along:11,alreadi:13,also:[1,3,6,11],altern:6,although:[6,16],alwai:[0,11],andconstraint:11,ani:[3,4,8,9,11,12,13,14,16],anoth:[8,11],applic:[9,14],arbitrarili:4,arch:12,arena:[5,12,16],arg:16,assign:6,astctl:7,astdiskd:[6,10,12,13,14,16],astmetad:[4,10,13,14,16],astoria:[0,1,2,3,4,5,6,7,9,11,12,13,14,16],astoria_vers:[3,12],astprocd:[10,14,16],asttestd:14,async:[11,12,13,14],asynchron:5,asyncio:[13,14],atlassian:6,attr:4,attribut:[4,12],automat:11,automount:16,avail:[3,11,13,14,16],avoid:5,await:14,background:[2,15],bar:4,base:[0,3,5,12,14,16],becom:14,bee:4,beeeeee:0,been:[5,11],befor:9,behaviour:9,below:0,between:[3,9],block_devic:11,bool:[3,11,12,14],both:[3,11],branch:[0,6],broadcast_ev:3,broadcastev:3,broadcasthelp:3,broker:[3,6,9,16],bug:[0,5],build:[0,6],built:0,bundl:[2,13,15],buster:16,calcul:[12,13],call:[9,13,16],callback:[5,10],can:[0,3,4,5,6,8,9,11,12,13,14,15,16],cannot:4,captur:[0,13],certain:11,chang:[0,3,6,11,13,14],check:[0,11],child:13,choic:6,classmethod:[11,12],clean:13,cleanup:11,clear:3,click:14,client:3,clone:6,code:[1,2,4,5,6,13,15],code_crash:13,code_finish:13,code_kil:13,code_run:13,code_start:13,code_statu:13,codestatu:13,combin:11,comm:1,command:[5,6,8,10,14,15],commit:0,common:[3,4,9,11,12,13,14],commun:[1,2,11,15],comp:[12,16],compar:[0,11],compat:16,compen:3,competit:[0,5],complex:5,compon:[3,5,10,11,12,13,14,15,16],concept:4,config:[12,14,16],config_fil:[11,12,13,14],configur:[12,15],conform:[3,4],connect:9,constaint:11,constructor:11,consum:[7,9,10,14,15],contain:[0,1,2,3,11,15,16],content:[2,10],contributor:15,control:5,cov:6,cover:6,coverag:6,crash:13,creat:11,current:[3,4,6,11,12],customis:9,daemon:[12,14],data:[3,4,5,8,10,14,15,16],dbu:[1,6,11,16],debian:16,debug:[7,11],def:14,defin:[3,4,13],definit:3,deliv:5,depend:[3,5,6,10,12,13],deploi:16,deploy:16,describ:16,design:[15,16],detail:7,determin:11,determine_disk_typ:11,dev:[0,6,12],develop:[0,1,4,5,15,16],dfeet:11,diagram:13,dict:[4,11],differ:[0,9],directori:13,disabl:5,disallow:3,disconnect:[3,9],disk:[13,16],disk_constraint:11,disk_info:[12,13],disk_typ:11,diskinfo:[11,13],diskmanag:11,diskmanagermessag:11,disktyp:11,diskuuid:11,dispatch:11,distribut:12,doc:6,document:[7,15,16],doe:[3,6,8,11],doesn:0,drive:[1,5,12,13],duplic:6,dure:4,dynam:4,each:[11,12],effect:4,either:11,enabl:5,enable_tl:16,enough:7,ensur:[3,6,11,12,13,14],enter:6,entiti:8,entrypoint:[0,9,14],environ:[4,6],epoch:0,equival:1,even:[4,13],event:9,event_nam:3,everi:[3,7,9],exampl:[4,16],exchang:3,execut:[1,6,13,15],exist:[6,11,13,14],explan:16,express:0,extens:6,extract:13,facili:3,fals:[11,16],falseconstraint:11,file:[0,11,14,15,16],filenam:11,filepresentconstraint:11,filesystem:11,find:[6,11],finish:13,first:[1,4,11],fix:0,flag:3,flake8:6,folder:6,follow:[0,5,6,12,13],foo:4,force_protocol_version_3_1:16,fork:6,format:[2,15,16],found:[6,11],freedesktop:11,from:[0,1,4,6,8,11,12,13,14],full:11,futur:5,game_timeout:[12,16],gen:15,gener:[4,6,15],get_current_metadata:12,get_event_loop:14,getlogg:14,git:[0,6],github:6,give:4,given:[11,12],gnu:6,goe:[11,12,13,14],good:[6,16],graphviz:6,group:0,guid:6,had:[1,12],handl:[5,9,12,13],handle_disk_insert:[12,13],handle_disk_remov:[12,13],handle_kill_request:13,handle_mutation_request:12,handle_restart_request:13,has:[6,11,12],hash:0,hat:5,have:[3,4,5,6,11,15,16],heavi:1,help:6,here:[4,6],herein:5,high:[2,12,16],higher:6,highest:4,hive:4,hold:8,host:16,how:11,html:6,http:1,ideal:16,identif:16,identifi:[0,3,11],ignor:[12,13],imag:0,immedi:3,immut:4,implement:[4,5,7,11,13,15],includ:4,incorpor:5,increment:0,indic:[0,4],individu:7,info:0,inform:[3,7,8,11,12,13,15,16],init:12,initi:4,initialis:[11,12],insert:[1,5,11,12,13],insid:6,inspect:7,inspir:1,instal:[1,6,16],integr:[5,6],intend:7,inter:[2,15],interact:[11,16],interfac:[5,8,10,16],introduc:4,ipc:3,is_flag:14,isol:1,issu:6,its:[3,12,14],job:11,json:[3,16],kei:4,kernel_vers:12,keyboard:16,kill:13,kit:[1,15,16],kit_nam:12,kit_vers:12,languag:5,last:[3,4,11],later:16,learn:6,least:[3,16],led:5,less:1,level:2,libc_ver:12,librari:[11,16],licenc:15,licens:15,line:[5,8,10,15],linter:6,linux:16,list:[8,11,14,15,16],listen:[3,11],live:5,load:12,local:6,locat:[13,16],log:[13,14],logger:[13,14],look:16,loop:[5,9,14],lower:4,machin:6,made:16,mai:16,main:[0,6,11,12,13,14],mainli:7,major:0,make:[5,6,8,13],manag:[1,4,6,8,9,10,11,12,15,16],manager_nam:3,manager_request:3,managermessag:[3,14],managerrequest:3,manifest:13,manual:6,master:0,match:[0,3,11],mean:[3,5],mechan:5,meet:6,member:11,messag:[4,11,12,13,14],metadata:[2,5,11,15],metadatamanag:12,metadatamanagermessag:12,method:[9,11],middl:3,minim:10,minor:0,mit:15,mode:[0,4,5,6,12,16],modul:13,modular:[1,5],more:[12,15],mosquitto:[6,16],mount:[11,16],mount_path:11,mous:16,mqtt:[3,6,9,14,16],multipl:[3,13],must:[3,4,6,8,9,11,14],mutabl:4,mutat:[3,8,12,13,14],mvp:5,mypi:6,name:[0,4,11,12,13,14,16],need:[0,3,6,8,11,16],neg:13,negat:11,network:0,newli:11,next:[3,11],noaction:11,non:0,none:[4,11,12,13,14],notconstraint:11,notic:11,now:6,nspawn:1,number:[4,6,11],numberoffilesconstraint:11,object:11,observ:11,occur:[3,6],off:5,offlin:[11,12,13,14],offline_statu:[11,12,13,14],onc:[12,16],one:[6,11,12,13],onli:[0,1,11,12,13],open:[1,6],oper:16,option:[6,12,13,14,16],orconstraint:11,order:[4,11,12],org:11,origin:[1,3],other:[5,11,12,13,14,16],our:6,out:[0,5],output:6,outsid:[0,16],over:[3,5,11],overlai:[4,12],overlaid:4,overrid:[4,16],overridden:4,overriden:[9,12],overview:2,packag:[6,16],page:16,paramet:11,partial:1,pass:14,password:0,patch:0,path:[11,13,14,16],pathlib:11,peopl:15,pep:6,perform:6,permit:12,persist:8,pip:6,place:16,pleas:[6,7,15],plod:5,poetri:6,point:11,poll:5,popul:12,port:[1,16],posix:16,possibl:[5,13,16],power:5,predecessor:1,present:[0,4,11],prioriti:[3,4,12,16],process:[2,14,15,16],processmanag:13,processmanagermessag:13,program:[8,11,14,16],programmat:[5,11],progress:13,project:[6,15],proper:16,properti:[11,12,13,14],protocol:[3,5],prototyp:1,provid:[5,7],proxi:3,pub:3,publish:[3,8,11,12,13,14],pull:6,pure:11,purpos:3,pydant:[5,12],pytest:6,python3:6,python:[1,5,6,11,16],python_vers:12,read:11,real:13,reason:3,receiv:[3,5,11,13],recognis:16,recommend:[11,16],refer:[5,16],refus:0,regex:0,regist:4,regular:0,reject:[0,3],relat:3,releas:[0,15],relev:11,reli:[11,12,13,14],remot:5,remov:[11,12,13],repli:3,repositori:6,repres:9,request:[6,8,12,13],requestrespons:[3,12,13],requir:[2,6,8,15],resolv:[4,12],resourc:6,respons:[3,11,12,13],restart:13,retain:3,robocon:1,robot:[0,1,3,4,5,15,16],robotd:1,robotmod:12,routin:[11,12,13,14],run:[0,3,4,5,6,9,12,13,14,15],run_until_complet:14,runtim:4,safe:[3,11,12,13,14],same:[3,16],schema:[3,4,5],scope:16,script:1,second:[4,11,13],section:2,see:[0,7,12,15,16],self:14,semver:0,send:13,sender_nam:3,sent:[0,3],seri:0,serv:6,set:[4,5,12,15],setup:16,shelf:5,shell:6,should:[0,3,4,6,7,8,11,12,13,14,16],sigchld:13,sigkil:13,signal:11,signifi:3,sigterm:13,simpl:[1,6,7],simultan:3,singl:3,softwar:[5,12],solut:5,some:[6,11,14],someth:[0,6],sourc:[1,3,11,12,13,16],sourcebot:1,spec:0,specif:[0,3,4,13],specifi:16,sphinx:6,spuriou:[4,11],srv4:1,ssid:0,stage:9,standalon:9,standard:[5,6],start:[1,4,5,13],startup:11,state:[3,4,7,9,10,11,12,13,15,16],statemanag:14,statement:6,statu:[3,5,11,12,13,14],stderr:13,stdout:13,still:13,stop:[3,13,14],store:[14,16],str:[3,4,11,12,14],stream:5,string:0,student:[0,5,15],style:5,sub:3,submit:6,subprocess:13,subscrib:[3,8,14],success:3,suit:6,superced:1,superclass:9,support:[0,1,16],system:[1,11,12,15],systemd:[1,16],take:[1,11,12],target:16,task:[11,13],tcp:3,team:0,technic:4,tell:6,temporari:13,term:4,test:[0,14,15,16],testament:3,testd:14,testmanag:14,than:5,thei:16,them:11,thi:[1,2,3,8,11,12,13,14,15,16],though:4,three:3,time:[12,13],tmux:16,toml:[0,16],too:5,topic:3,topic_prefix:16,tradit:16,trigger:13,trueconstraint:11,tutori:6,type:[4,11,12,13,14],udisk:[11,16],udiski:[6,11,16],udisks2:[6,11],under:15,understand:7,uniqu:3,unknown:0,unpack:13,updat:[0,1,5,11,12,13],update_st:11,update_statu:[12,13],upgrad:8,usag:[5,7,15],usb:[1,4,5,13,15],use:[6,16],used:[0,3,4,6,11],useful:11,user:[0,16],usercod:[11,16],uses:[1,3,11],using:[0,3,5,6,11,16],util:16,uuid:[3,11,12,13],valid:[12,13],validate_assign:12,valu:[4,11,12,13],variou:9,verbos:[11,12,13,14],verifi:13,version:[3,16],via:13,view:6,virtual:6,volum:11,volunt:0,wait:[3,12,13,14],wait_loop:14,wamp:1,warn:[0,4],wasp:4,web:[3,5],websocket:3,were:5,when:[5,11,12,13,14],where:[4,5],wherebi:12,which:[4,11],whilst:14,who:15,wifi:0,wifi_en:[12,16],wifi_password:[0,12],wifi_ssid:[0,12],wireless:5,wish:6,within:[6,13],without:[3,7],work:[1,6],workaround:5,write:[6,13],written:5,yaml:0,year:0,you:[6,16],your:6,yourself:6,zip:[0,16],zone:[4,12,16]},titles:["Code Bundle Format","Background","Design","Inter-Process Communication","Metadatas","Design Requirements","Development","Command Line Interface","State Consumers","Data Components","Implementation","Astdiskd","Astmetad","Astprocd","State Managers","Astoria","Usage"],titleterms:{"class":[11,12,13],"static":6,addit:5,astctl:16,astdiskd:11,astmetad:12,astoria:15,astprocd:13,background:1,broadcast:3,bundl:0,callback:9,check:6,code:0,command:[7,16],commun:3,compon:9,configur:16,constraint:11,consum:8,contribut:15,data:[9,11,12,13],definit:11,depend:14,design:[2,5],detect:11,develop:6,disk:[11,12],document:6,drive:11,event:3,exampl:0,format:0,herdsman:1,identif:11,implement:10,inter:3,interfac:7,kit:0,lifecycl:[12,13],line:[7,16],lint:6,manag:[3,13,14],messag:3,metadata:[4,12,16],minim:14,minimum:5,pepper2:1,process:[3,13],request:3,requir:[5,16],resolut:4,run:16,runusb:1,set:6,shepherd:1,sourc:4,state:[8,14],structur:[11,12,13],system:16,target:0,technic:5,test:6,type:[3,6],unit:6,usag:16,usb:16,usercod:13,version:0}})
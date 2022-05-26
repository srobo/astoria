Search.setIndex({docnames:["design/history","design/index","design/ipc","design/metadata","design/requirements","design/usercode_drives","development/index","implementation/consumers/astctl","implementation/consumers/astwifid","implementation/consumers/index","implementation/data_components","implementation/disk_types","implementation/index","implementation/managers/astdiskd","implementation/managers/astmetad","implementation/managers/astprocd","implementation/managers/index","index","usage"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":5,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,"sphinx.ext.intersphinx":1,"sphinx.ext.viewcode":1,sphinx:56},filenames:["design/history.rst","design/index.rst","design/ipc.rst","design/metadata.rst","design/requirements.rst","design/usercode_drives.rst","development/index.rst","implementation/consumers/astctl.rst","implementation/consumers/astwifid.rst","implementation/consumers/index.rst","implementation/data_components.rst","implementation/disk_types.rst","implementation/index.rst","implementation/managers/astdiskd.rst","implementation/managers/astmetad.rst","implementation/managers/astprocd.rst","implementation/managers/index.rst","index.rst","usage.rst"],objects:{"astoria.astdiskd":[[13,0,1,"","DiskManager"]],"astoria.astdiskd.DiskManager":[[13,1,1,"","main"],[13,2,1,"","name"],[13,3,1,"","offline_status"],[13,1,1,"","update_state"]],"astoria.astprocd":[[15,0,1,"","ProcessManager"]],"astoria.astprocd.ProcessManager":[[15,2,1,"","dependencies"],[15,1,1,"","handle_astmetad_message"],[15,1,1,"","handle_disk_insertion"],[15,1,1,"","handle_disk_removal"],[15,1,1,"","handle_kill_request"],[15,1,1,"","handle_restart_request"],[15,1,1,"","main"],[15,2,1,"","name"],[15,3,1,"","offline_status"],[15,1,1,"","update_status"]],"astoria.astwifid":[[8,0,1,"","WiFiHotspotLifeCycle"]],"astoria.astwifid.WiFiHotspotLifeCycle":[[8,2,1,"","HOSTAPD_BINARY"],[8,1,1,"","__init__"],[8,1,1,"","generate_hostapd_config"],[8,1,1,"","has_metadata_changed"],[8,1,1,"","run_hotspot"],[8,1,1,"","stop_hotspot"]],"astoria.common.code_status":[[15,0,1,"","CodeStatus"]],"astoria.common.code_status.CodeStatus":[[15,2,1,"","CRASHED"],[15,2,1,"","FINISHED"],[15,2,1,"","KILLED"],[15,2,1,"","RUNNING"],[15,2,1,"","STARTING"]],"astoria.common.disks":[[13,0,1,"","DiskInfo"],[11,0,1,"","DiskType"],[11,0,1,"","DiskTypeCalculator"],[13,0,1,"","DiskUUID"]],"astoria.common.disks.DiskInfo":[[13,2,1,"","disk_type"],[13,2,1,"","mount_path"],[13,2,1,"","uuid"]],"astoria.common.disks.DiskType":[[11,2,1,"","METADATA"],[11,2,1,"","NOACTION"],[11,2,1,"","UPDATE"],[11,2,1,"","USERCODE"]],"astoria.common.disks.DiskTypeCalculator":[[11,1,1,"","__init__"],[11,1,1,"","calculate"]],"astoria.common.disks.constraints":[[11,0,1,"","AndConstraint"],[11,0,1,"","Constraint"],[11,0,1,"","FalseConstraint"],[11,0,1,"","FilePresentConstraint"],[11,0,1,"","NotConstraint"],[11,0,1,"","NumberOfFilesConstraint"],[11,0,1,"","OrConstraint"],[11,0,1,"","TrueConstraint"]],"astoria.common.disks.constraints.AndConstraint":[[11,1,1,"","__init__"],[11,1,1,"","matches"]],"astoria.common.disks.constraints.Constraint":[[11,1,1,"","matches"]],"astoria.common.disks.constraints.FalseConstraint":[[11,1,1,"","matches"]],"astoria.common.disks.constraints.FilePresentConstraint":[[11,1,1,"","__init__"],[11,1,1,"","matches"]],"astoria.common.disks.constraints.NotConstraint":[[11,1,1,"","__init__"],[11,1,1,"","matches"]],"astoria.common.disks.constraints.NumberOfFilesConstraint":[[11,1,1,"","__init__"],[11,1,1,"","matches"]],"astoria.common.disks.constraints.OrConstraint":[[11,1,1,"","__init__"],[11,1,1,"","matches"]],"astoria.common.disks.constraints.TrueConstraint":[[11,1,1,"","matches"]],"astoria.common.ipc":[[13,0,1,"","DiskManagerMessage"],[2,0,1,"","ManagerRequest"],[14,0,1,"","MetadataManagerMessage"],[15,0,1,"","ProcessManagerMessage"],[2,0,1,"","RequestResponse"]],"astoria.common.ipc.DiskManagerMessage":[[13,1,1,"","calculate_disk_info"],[13,2,1,"","disks"]],"astoria.common.ipc.ManagerRequest":[[2,2,1,"","sender_name"],[2,2,1,"","uuid"]],"astoria.common.ipc.MetadataManagerMessage":[[14,2,1,"","metadata"]],"astoria.common.ipc.ProcessManagerMessage":[[15,2,1,"","code_status"],[15,2,1,"","disk_info"]],"astoria.common.ipc.RequestResponse":[[2,2,1,"","reason"],[2,2,1,"","success"],[2,2,1,"","uuid"]],"astoria.common.metadata":[[14,0,1,"","Metadata"],[14,0,1,"","RobotMode"]],"astoria.common.metadata.Metadata":[[14,0,1,"","Config"],[14,2,1,"","arch"],[14,2,1,"","arena"],[14,2,1,"","astoria_version"],[14,2,1,"","game_timeout"],[14,1,1,"","init"],[14,1,1,"","is_wifi_valid"],[14,2,1,"","kernel_version"],[14,2,1,"","libc_ver"],[14,2,1,"","marker_offset"],[14,2,1,"","mode"],[14,2,1,"","python_version"],[14,2,1,"","usercode_entrypoint"],[14,2,1,"","wifi_enabled"],[14,2,1,"","wifi_psk"],[14,2,1,"","wifi_region"],[14,2,1,"","wifi_ssid"],[14,2,1,"","zone"]],"astoria.common.metadata.Metadata.Config":[[14,2,1,"","validate_assignment"]],"astoria.common.metadata.RobotMode":[[14,2,1,"","COMP"],[14,2,1,"","DEV"]]},objnames:{"0":["py","class","Python class"],"1":["py","method","Python method"],"2":["py","attribute","Python attribute"],"3":["py","property","Python property"]},objtypes:{"0":"py:class","1":"py:method","2":"py:attribute","3":"py:property"},terms:{"0":3,"1":[3,5,18],"120":18,"123":18,"1883":[6,18],"2":[3,5,13,18],"2022":17,"3":[3,6,18],"3166":5,"5":15,"6":[6,18],"8":6,"9001":6,"abstract":11,"boolean":14,"case":[5,15],"class":[2,12,16],"default":[11,13,18],"do":[2,6,18],"final":2,"function":[9,10],"import":16,"int":[11,14],"long":18,"new":15,"public":[2,6],"return":[8,11,13,14,15,16],"static":18,"true":[5,8,11,14,16,18],"var":18,"while":8,A:[0,2,3,5,6,9,10,11,13,15,16,18],As:[11,13],For:[3,7,17,18],If:[5,6,8,9,18],It:[0,2,5,7,8,10,13,15,18],No:[3,11],Not:[0,11],On:13,The:[2,3,4,5,6,10,11,15,17,18],There:[2,14,18],These:[4,8],To:15,_:11,__init__:[8,11],__main__:16,__name__:16,_init:16,_post_connect:10,_post_disconnect:10,_pre_connect:10,_pre_disconnect:10,abc1:5,abil:4,abl:3,about:[2,13,18],abov:[4,15],access:[6,8],accident:6,accord:5,action:[2,11],ad:14,addit:[2,14,15],after:[2,8,10],against:11,aim:4,alert:2,all:[0,2,3,6,18],allow:[2,4,8,11,16],along:11,alpha:5,alreadi:[5,15],also:[0,2,5,6],altern:6,although:[6,18],alwai:11,an:[0,2,3,4,6,7,18],andconstraint:11,ani:[2,3,8,9,10,13,14,15,16,18],anoth:[9,13],ap:8,applic:[6,10,16],ar:[2,3,4,6,8,11,13,14,15,16,18],arbitrarili:3,arch:14,arena:[4,14,18],arg:18,assign:6,astctl:7,astdiskd:[6,11,12,14,15,16,18],astmetad:[3,8,12,15,16,18],astoria:[0,1,2,3,4,5,6,7,8,10,11,13,14,15,16,18],astoria_vers:[2,14],astprocd:[12,16,18],asttestd:16,astwifid:[9,12],async:[8,13,15,16],asynchron:4,asyncio:[8,15,16],atlassian:6,attach:11,attr:3,attribut:3,automat:[5,8,13],automount:18,avail:[2,11,15,16,18],avoid:4,await:16,b:11,background:[1,17],bar:3,base:[2,4,8,14,18],becom:16,bee:3,been:4,befor:10,behaviour:10,between:[2,10],block_devic:13,bool:[2,8,11,14,16],both:[2,11],br0:18,branch:6,bridg:[8,18],broadcast:5,broadcast_ev:2,broadcastev:2,broadcasthelp:2,broker:[2,6,10,18],bug:4,build:6,bundl:[5,8],buster:18,c:[16,18],cach:8,cache_dir:18,calcul:[11,13,15],calculate_disk_info:13,call:[10,15,18],callback:[4,12],can:[2,3,4,5,6,9,10,11,14,15,16,17,18],cannot:3,captur:15,certain:11,chang:[2,5,6,8,13,15,16],check:[8,11,14],child:[8,15],choic:6,classmethod:14,clean:15,cleanup:13,clear:2,click:16,client:2,clone:6,code:[0,3,4,5,6,8,15],code_crash:15,code_finish:15,code_kil:15,code_run:15,code_start:15,code_statu:15,codestatu:15,combin:11,come:8,comm:0,command:[4,6,9,12,16,17],common:[2,3,10,11,13,14,15,16],commun:[0,1,13,17],comp:[14,18],compar:11,compat:18,compen:2,competit:[4,5],complex:4,complianc:5,compon:[2,4,8,11,12,13,15,16,17,18],compos:6,concept:3,config:[11,13,14,16,18],config_fil:[13,15,16],configur:[5,8,14,17],conform:[2,3],connect:10,constaint:11,constraint:12,constructor:11,consum:[7,10,12,16,17],contain:[0,1,2,5,11,17,18],contributor:17,control:[4,5],cov:6,cover:6,coverag:6,crash:15,creat:[5,8,11],credenti:[5,8],current:[2,3,6,8,13],current_cod:5,customis:10,daemon:[14,16],data:[2,3,4,9,11,12,16,17,18],dbu:[0,6,13,18],debian:18,debug:[7,13],def:16,default_usercode_entrypoint:[11,13,18],defin:[2,3,15],definit:[2,12],deliv:4,depend:[2,4,6,12,15],deploi:18,deploy:18,describ:18,design:[17,18],detail:7,detect:11,determin:11,dev:[6,14],develop:[0,3,4,8,17],devic:5,dfeet:13,dhcp:8,diagram:15,dict:[3,13],dictionari:13,differ:10,directori:[15,18],disabl:4,disallow:2,disconnect:[2,10],disk:[12,13,15,17,18],disk_info:15,disk_typ:13,diskinfo:[13,15],diskmanag:13,diskmanagermessag:13,disktyp:[11,13],disktypecalcul:11,diskuuid:13,dispatch:13,distribut:14,doc:6,docker:17,dockerfil:6,document:[7,18],doe:[2,5,6,9,11],drive:[0,1,4,11,14,15,17],duplic:6,dure:3,dynam:[3,8],e:[4,5],each:[11,13],effect:3,either:11,en:5,enabl:[4,14],enable_tl:18,enable_wpa3:[8,18],enough:7,ensur:[2,6,11,13,15,16],enter:6,entiti:9,entrypoint:[10,11,13,16],env:18,environ:[3,6],equival:0,even:[3,15],event:10,event_nam:2,everi:[2,7,10],exampl:[3,5,18],example_env_var:18,exchang:2,execut:[0,5,6,15,17],exist:[5,6,11,15,16],explan:18,expos:6,extens:6,f:6,facili:2,fals:[5,8,11,18],falseconstraint:11,few:11,file:[8,11,16,17,18],filenam:11,filepresentconstraint:11,filesystem:13,find:[6,11],finish:15,first:[0,3,11],flag:2,flake8:6,folder:6,follow:[4,6,14,15],foo:3,force_protocol_version_3_1:18,fork:6,format:[5,18],found:[6,11],freedesktop:13,from:[0,3,6,8,9,11,13,14,15,16],full:11,futur:4,g:4,game_timeout:[14,18],gb:5,gen:17,gener:[3,6,8,17],generate_hostapd_config:8,get_event_loop:16,getlogg:16,git:6,github:6,give:[3,13],given:[11,14],gnu:6,go:[13,15,16],goe:[13,15,16],good:[6,18],graphviz:6,guid:6,ha:[6,14],had:[0,14],handl:[4,8,10,15],handle_astmetad_messag:15,handle_disk_insert:15,handle_disk_remov:15,handle_kill_request:15,handle_restart_request:15,has_metadata_chang:8,hat:4,have:[2,3,4,6,11,17,18],heavi:0,help:6,helper:11,here:[3,6],herein:4,high:[1,14,18],higher:6,highest:3,hive:3,hold:9,host:[6,8,18],hostapd:8,hostapd_binari:8,hotspot:8,howev:5,hr:0,html:6,http:[0,5],i:[4,5],id:6,ideal:18,identif:[12,18],identifi:2,ignor:[5,14,15],immedi:2,immut:3,implement:[3,4,7,11,15,17],includ:[3,6],incorpor:4,indic:[3,14],individu:[7,11],info:[13,15],inform:[2,5,7,8,9,13,14,15,17,18],init:14,initi:3,initialis:[11,14],insert:[0,4,13,14,15],insid:6,inspect:7,inspir:0,instal:[0,6,18],integr:[4,6],intend:7,inter:[1,17],interact:[13,18],interfac:[4,6,8,9,12,18],introduc:3,ipc:[2,13,14,15,16],is_flag:16,is_wifi_valid:14,iso:5,iso_3166:5,isol:0,issu:6,its:[2,14,16],itself:11,job:13,js:4,json:[2,18],kei:[3,5],kernel_vers:14,keyboard:18,kgiwtnnmdfnd:5,kill:[8,15],kit:[0,5,8,17],languag:4,last:[2,3,11],later:18,launch:8,learn:6,least:[2,18],led:4,less:0,level:1,libc_ver:14,librari:[13,18],licenc:17,licens:17,lifecycl:8,line:[4,9,12,17],linter:6,linux:18,list:[11,13,17,18],listen:[2,13],live:4,load:14,local:6,locat:[15,18],log:[15,16],logger:[15,16],look:18,loop:[4,10,16],lower:3,machin:6,made:18,mai:18,main:[6,13,15,16],mainli:7,major:5,make:[4,6,9,15],manag:[0,3,6,8,9,10,12,13,14,17,18],manager_messag:[13,15],manager_nam:2,managermessag:[2,16],managerrequest:2,manifest:15,manual:6,marker_offset:14,mass:5,match:[2,8,11,15],mean:[2,4],mechan:[4,5],meet:6,member:11,messag:[13,14,15],metadata:[1,4,5,8,11,17],metadatamanagermessag:14,method:10,middl:2,minim:12,mit:17,mode:[3,4,5,6,8,14,18],modul:[8,15],modular:[0,4],more:[14,17],mosquitto:[6,18],mount:[11,13,18],mount_path:13,mous:18,mqtt:[2,6,10,16,18],multipl:[2,15],must:[2,3,5,6,9,10,11,16],mutabl:3,mutat:[2,9,15,16],mvp:4,mypi:6,n:11,name:[3,11,13,15,16],need:[2,6,9,13,18],neg:15,negat:11,network:[5,8],newli:13,newtyp:13,next:[2,13],noaction:11,none:[3,8,13,15,16],notconstraint:11,notic:13,now:6,nspawn:0,number:[3,6,11],numberoffilesconstraint:11,object:13,observ:13,occur:[2,6],off:4,offlin:[13,15,16],offline_statu:[13,15,16],onc:[14,18],one:[6,11,14,15],onli:[0,11,13,14,15],open:[0,6],oper:[6,8,18],option:[6,14,15,16,18],orconstraint:11,order:[3,11],org:[5,13],origin:[0,2],os:18,other:[4,8,11,13,15,16,18],our:6,out:4,output:6,outsid:18,over:[2,4,13],overlai:3,overlaid:3,overrid:[3,5,18],overridden:[3,5],overriden:10,overview:1,packag:[6,18],page:18,param:14,paramet:[11,13],partial:0,pass:16,path:[11,13,15,16,18],pathlib:13,payload:15,peopl:17,pep:6,perform:6,persist:9,pip:6,place:18,pleas:[6,7,17],plod:4,poetri:6,point:[8,11],poll:4,popul:14,port:[0,6,18],posix:18,possibl:[4,15,18],power:4,predecessor:0,presenc:8,present:[3,11],prioriti:[2,3,14,18],process:[1,8,16,17,18],processmanag:15,processmanagermessag:15,product:18,program:[9,13,16,18],programmat:[4,11],progress:15,project:[6,17],proper:18,properti:[8,13,15,16],protocol:[2,4],prototyp:0,provid:[4,7,8],proxi:2,psk:8,pub:2,publish:[2,9,13,14,15,16],pull:6,pure:13,purpos:2,py:[5,6,18],pydant:[4,14],pytest:6,python3:[5,6],python:[0,4,5,6,13,18],python_vers:14,read:13,real:15,reason:2,receiv:[2,4,8,13,15],recognis:18,recommend:[13,18],ref:8,refer:[4,18],region:[5,8],regist:3,reject:2,relat:2,releas:17,relev:11,reli:[11,13,15,16],remot:4,remov:[13,15],repli:2,repositori:6,repres:10,request:[6,9,15],requestrespons:[2,15],requir:[1,5,6,8,9,17],resolv:[3,14],resourc:6,respons:[2,8,11,13,14,15],restart:[8,15],retain:2,robocon:0,robot:[0,2,3,4,17,18],robotd:0,robotmod:14,routin:[13,15,16],rtype:14,run:[2,3,4,8,10,14,15,16,17],run_hotspot:8,run_until_complet:16,runtim:3,s:[0,2,8,11,16],safe:[2,13,15,16],same:[2,18],sb:4,schema:[2,3,4],scope:18,script:0,second:[3,11,15],section:1,see:[7,14,17,18],self:16,send:15,sender_nam:2,sent:2,serv:6,set:[3,4,8,14,17],setup:18,shelf:4,shell:6,should:[2,3,5,6,7,9,11,13,15,16,18],sigchld:15,sigkil:15,signal:13,signifi:2,sigterm:15,simpl:[0,6,7],simultan:2,singl:2,so:[2,15,16],softwar:[4,14],solut:4,some:[6,11,16],someth:6,sort:11,sourc:[0,2,8,11,13,14,15,18],sourcebot:0,specif:[2,3,15],specifi:[5,18],sphinx:6,spuriou:[3,11],srv4:0,ssid:8,stage:10,standalon:10,standard:[4,5,6],start:[0,3,4,8,15],startup:13,state:[2,3,7,10,12,13,14,15,17,18],statemanag:16,statement:6,statu:[2,4,13,14,15,16],stderr:15,stdout:15,still:15,stop:[2,8,15,16],stop_hotspot:8,storag:5,store:[8,16,18],str:[2,3,8,11,13,14,16],stream:4,struct:[13,15],student:[4,17],style:4,sub:2,submit:6,subprocess:[5,8,15],subscrib:[2,9,16],success:2,suit:6,superced:0,superclass:10,support:[0,18],system:[0,8,11,13,17],systemd:[0,18],take:[0,11],target:18,task:[13,15],tcp:2,team_tla:5,technic:3,tell:6,temporari:15,term:3,test:[16,17,18],testament:2,testd:16,testmanag:16,than:4,thei:18,them:13,thi:[0,1,2,5,6,8,9,11,13,14,15,16,17,18],though:3,three:2,time:[14,15],tmp:8,tmux:18,toml:[5,18],too:[4,5],topic:2,topic_prefix:18,tradit:18,trigger:15,trueconstraint:11,ts:4,turn:14,tutori:6,type:[3,8,12,13,14,15,16,17],u:5,udisk:[13,18],udiski:[6,13,18],udisks2:[6,13],ui:[2,4],unbuff:5,under:17,understand:7,uniqu:2,up:[8,15,17],updat:[0,4,8,11,13,15],update_st:13,update_statu:15,upgrad:9,us:[0,2,3,4,5,6,8,11,13,15,18],usag:[4,7,17],usb:[0,3,4,5,8,15,17],user:[5,18],usercod:[1,8,11,17,18],usercode_entrypoint:[5,14],usual:5,util:18,uuid:[2,13,15],v:16,valid:14,validate_assign:14,valu:[3,5,11,14,15],variou:10,verbos:[13,15,16],version:2,via:[8,15],view:6,virtual:6,volum:13,wa:0,wait:[2,14,15,16],wait_loop:16,wamp:0,warn:3,wasp:3,we:[4,6,13],web:[2,4],websocket:[2,6],were:4,what:11,when:[4,11,13,14,15,16],where:[3,4],whether:14,which:[3,5,11],whilst:[11,16],who:17,wifi:[8,14,18],wifi_en:[5,8,14,18],wifi_psk:[5,14],wifi_region:[5,14],wifi_ssid:14,wifihotspotlifecycl:8,wiki:5,wikipedia:5,wireless:4,wish:6,within:[6,15],without:[2,7,8],wlan0:18,work:[0,6],workaround:4,write:[6,15],written:4,x:13,yml:6,you:[5,6,18],your:6,yourself:6,zip:18,zone:[3,14,18]},titles:["Background","Design","Inter-Process Communication","Metadatas","Design Requirements","Usercode Drives","Development","Command Line Interface","Astwifid","State Consumers","Data Components","Disk Types","Implementation","Astdiskd","Astmetad","Astprocd","State Managers","Astoria","Usage"],titleterms:{"class":[8,11,13,14,15],"static":6,addit:4,astctl:18,astdiskd:13,astmetad:14,astoria:17,astprocd:15,astwifid:8,background:0,broadcast:2,callback:10,check:6,command:[7,18],commun:2,compon:10,configur:18,constraint:11,consum:9,content:[1,12],contribut:17,data:[8,10,13,14,15],definit:11,depend:16,design:[1,4],detect:13,develop:6,disk:[11,14],docker:6,document:[6,17],drive:[5,13],entrypoint:5,event:2,file:5,herdsman:0,identif:11,implement:12,inter:2,interfac:7,lifecycl:[14,15],line:[7,18],lint:6,list:[9,16],manag:[2,15,16],messag:2,metadata:[3,14,18],minim:16,minimum:4,pepper2:0,process:[2,15],request:2,requir:[4,18],resolut:3,robot:5,run:[6,18],runusb:0,set:[5,6],shepherd:0,sourc:3,state:[9,16],structur:[8,13,14,15],system:18,technic:4,test:6,type:[2,6,11],unit:6,up:6,usag:18,usb:18,usercod:[5,15],wifi:5}})
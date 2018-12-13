
import requests, zipfile, io
import redis
import cherrypy
import os
zp='https://www.bseindia.com/download/BhavCopy/Equity/EQ121218_CSV.ZIP'

r = requests.get(zp)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall()

redis_host = os.environ.get('REDIS_HOST', 'localhost')   
redis_port = '6379'
redis_password = ""
CHANNEL_LAYERS = {
    "default": {

        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(redis_host, 6379)],
        },
        "ROUTING": "multichat.routing.channel_routing",
    },
}
import csv
names=[]
#*********************************************class to push into redis**************************


class zeroth:
    def hello_redis(self):  
    
        try:
            r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True) 
            line=csv.reader(open('EQ121218.CSV','r'))
            line=list(line)
            del line[0]   
          
            for x in line:
                user={"Code":x[0], "Name":x[1],"open":x[4],"high":x[5], "low":x[6], "close":x[7]}
              
                r.hmset(x[1].strip(),user)
                names.append(x[1].strip())
           
            return names,r  
                
        except Exception as e:
            print(e)


#******************************cherrypy to host ***************************************************

class index:
    z=zeroth()
    names,r=z.hello_redis()
    index=""
    inp=""
    
    
    @cherrypy.expose
    def index(self):
        res=""
        res+='<th>CODE</th>'+'<th>NAME</th>'+'<th>LOW</th>'+'<th>OPEN</th>'+'<th>HIGH</th>'
        name=self.names[0:10]
        for n in name:
            res+='<tr>'
            x1=dict()
            x1=self.r.hgetall(n)
            #print("x1--------------------------",x1)
            res+='<td>'+x1['Code']+'</td>'+'<td>'+x1['Name']+'</td>'+'<td>'+x1['low']+'</td>'+'<td>'+x1['open']+'</td>'+'<td>'+x1['high']+'</td>'
                
            res+='</tr>'
            
        tab="table (border-collapse: collapse;width: 80%;}tr:nth-child(even) {background-color: #f2f2f2;}"
        th='th, td {  padding: 8px;  text-align: left;  border-bottom: 1px solid #ddd;}'

        self.index =open("html/index.html").read().format(first_header=res,css_header=th+tab)
        try:
            self.inp= """
                <form method="post" action="redirect" >
                <p>Enter the name</p>
                <input type="text" name="name"><br>
                <br>
                <input type="submit" >
                """
        except:
            self.inp= """
                <form method="post" action="index" style="background-color:white;" >
                <p>Enter the name</p><tr>
                <input type="text" name="name">
                <input type="submit" ></tr>
                """
        return self.index,self.inp
            
    @cherrypy.expose() 
    def redirect(self,name):
        if name and name in self.names:
            res2=""
            #print(name)
            #print("---------------",self.r)
            #print("**********",self.r.hgetall("HDFC"))
            x1=self.r.hgetall(name)
            print(x1)
            
            res2+='<table style="background-color:white;position:absolute;top:20%;left:85%;"><tr><th>CODE</th><td>'+x1['Code']+'</td></tr>'  +'<tr><th>NAME</th><td>'+x1['Name']+'</td></tr>'+'<tr><th>LOW</th><td>'+x1['low']+'</td></tr>'+'<tr><th>OPEN</th><td>'+x1['open']+'</td></tr>'+'<tr><th>HIGH</th><td>'+x1['high']+'</td></tr>'
            res2+='</table>'
            return self.index,self.inp,res2
        else:
            erroe="Name not found"
            return self.index,self.inp,erroe
            
        
    
    
    
    

if __name__ == "__main__":
    cherrypy.config.update({'server.socket_host': '0.0.0.0',})
    cherrypy.config.update({'server.socket_port': int(os.environ.get('PORT', '5000')),})
    
    cherrypy.tree.mount(index())
    cherrypy.engine.start()
    cherrypy.engine.block()
'''
cherrypy.config.update({'server.socket_port': p,})
cherrypy.engine.start()
#cherrypy.quickstart(index())'''

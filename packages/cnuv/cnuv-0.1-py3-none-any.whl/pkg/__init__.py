def CSComm_1():
    s = """import java.net.*;
import java.io.*;
import java.util.*;

class dateserver
{
	public static void main(String args[])
	{
		ServerSocket ss;
		Socket s;
		PrintStream ps;
		DataInputStream dis;
		String inet;
		try 
		{
			ss = new ServerSocket(8020);
			while (true)
			{
			s = ss.accept();
			ps = new PrintStream(s.getOutputStream());
			Date d = new Date();
			ps.println(d);
			dis = new DataInputStream(s.getInputStream());
			inet = dis.readLine();
			System.out.println("THE CLIENT SYSTEM ADDRESS IS:" + inet);
			ps.close();
			}
		} 
		catch (IOException e) 
		{
			System.out.println("The Exception is :" + e);
		}
	}
}
"""
    c = """import java.net.*;
import java.io.*;
class dateclient 
{
	public static void main(String[] args) 
	{
		Socket soc;
		DataInputStream dis;
		String sdate;
		PrintStream ps;
		try
		{
			InetAddress ia=InetAddress.getLocalHost();
			soc=new Socket(ia,8020);
			dis=new DataInputStream(soc.getInputStream());
			sdate=dis.readLine();
			System.out.println("THE date in the server is:"+sdate);
			ps=new PrintStream(soc.getOutputStream());
			ps.println(ia);
		}
		catch(IOException e)
		{
			System.out.println("THE EXCEPTION is: "+e);		
		}
	}
}
"""
    return s,c

def PingAndTraceRoute_2():
    s = """import java.io.*;
import java.net.*;
class pingserver
{
public static void main(String args[])
{
try
{
String str;
System.out.print(" Enter the IP Address to be Ping : ");
DataInputStream dis=new DataInputStream(System.in);
String ip=dis.readLine();
Runtime H=Runtime.getRuntime();
Process p=H.exec("ping " + ip);
InputStream in=p.getInputStream();
DataInputStream buf2=new DataInputStream(in);
while((str=buf2.readLine())!=null)
{
System.out.println(" " + str);
}
}
catch(Exception e)
{

System.out.println(e.getMessage());
}
}}
"""
    c = """import java.io.*;
import java.net.*;

public class traceroutecmd {

     public static void runSystemCommand(String command)
     {
          try
          {
              Process p = Runtime.getRuntime().exec(command);
	DataInputStream inputstream=new DataInputStream(p.getInputStream());
              

              String s = "";
              while ((s = inputstream.readLine()) != null)
                   System.out.println(s);
          }
          catch (Exception e)
          {
          }}

     public static void main(String[] args)
     {  
          String ip = "www.google.co.in";
        
        
          runSystemCommand("tracert " + ip);
     }
}"""
    return s,c

def Upload_and_download_3():
    s = """import java.net.*;
import java.io.*;
import java.awt.image.*;
import javax.imageio.*;
import javax.swing.*;
class Server {
public static void main(String args[]) throws Exception{
ServerSocket server=null;
Socket socket;
server=new ServerSocket(4000);
System.out.println("Server Waiting for image");
socket=server.accept(); System.out.println("Client connected.");
InputStream in = socket.getInputStream();
DataInputStream dis = new DataInputStream(in);
int len = dis.readInt();
System.out.println("Image Size: " + len/1024 + "KB"); byte[] data = new byte[len];
dis.readFully(data);
dis.close();
in.close();
InputStream ian = new ByteArrayInputStream(data);
BufferedImage bImage = ImageIO.read(ian);
JFrame f = new JFrame("Server");
ImageIcon icon = new ImageIcon(bImage);
JLabel l = new JLabel();
l.setIcon(icon);
f.add(l);
f.pack();
f.setVisible(true);
}}
"""
    c = """import javax.swing.*;
import java.net.*;
import java.awt.image.*;
import javax.imageio.*;
import java.io.*;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException; import
javax.imageio.ImageIO;
public class Client{
public static void main(String args[]) throws Exception{
Socket soc;
BufferedImage img = null;
soc=new Socket("localhost",4000);
System.out.println("Client is running. ");
try {
System.out.println("Reading image from disk. ");
img = ImageIO.read(new File("dog.jpg"));
ByteArrayOutputStream baos = new ByteArrayOutputStream();
ImageIO.write(img, "jpg", baos);
baos.flush();
byte[] bytes = baos.toByteArray();
baos.close();
System.out.println("Sending image to server. ");
OutputStream out = soc.getOutputStream();
DataOutputStream dos = new DataOutputStream(out);
dos.writeInt(bytes.length);
dos.write(bytes, 0, bytes.length);
System.out.println("Image sent to server. ");
dos.close();
out.close();
}catch (Exception e) { System.out.println("Exception: " + e.getMessage());
soc.close();
}
soc.close();
}}
"""
    return s,c

def CRC_4():
    s = """import java.io.*;
class CRC
{
public static void main(String args[]) throws IOException
{
 
 System.out.println("Enter Generator:");
 DataInputStream br=new DataInputStream(System.in);
 String gen = br.readLine();
 System.out.println("Enter Data:");
 String data = br.readLine();
 String code = data;
 while(code.length() < (data.length() + gen.length() - 1))
{
 code = code + "0";
} 
code = data + div(code,gen);
 System.out.println("The transmitted Code Word is: " + code);
 System.out.println("Please enter the received Code Word: ");
 String rec = br.readLine();
 if(Integer.parseInt(div(rec,gen)) == 0)
 System.out.println("The received code word contains no errors.");
 else
 System.out.println("The received code word contains errors.");
}
static String div(String num1,String num2)
{
 int pointer = num2.length();
 String result = num1.substring(0, pointer);
 String remainder = "";
 for(int i = 0; i < num2.length(); i++)
 {
 if(result.charAt(i) == num2.charAt(i))
 remainder += "0";
 else
 remainder += "1";
 }
 while(pointer < num1.length())
 {
 if(remainder.charAt(0) == '0')
 {
 remainder = remainder.substring(1, remainder.length());
 remainder = remainder + String.valueOf(num1.charAt(pointer));
 pointer++;
 }
 result = remainder;
 remainder = "";
 for(int i = 0; i < num2.length(); i++)
 {
 if(result.charAt(i) == num2.charAt(i))
 remainder += "0";
 else
 remainder += "1";
 }
 }
 return remainder.substring(1,remainder.length());
}
}
"""
    return s

def StopAndWait_5():
    s = """import java.io.*;
import java.net.*;
import java.util.Scanner;
public class sender {
public static void main(String args[])
{
   int p=9000,i,q=8000;
    String h="localhost";
    try
    {
    Scanner scanner = new Scanner(System.in);
    System.out.print("Enter number of frames : ");
    int number = scanner.nextInt();
    if(number==0)
    {
        System.out.println("No frame is sent");
    }
    else
            {           

          Socket s2= new Socket(h,q);

        DataOutputStream d1 = new DataOutputStream(s2.getOutputStream());

        d1.write(number);

          }

    String str1;

        for (i=0;i<number;i++)

        {                 

    System.out.print("Enter message : ");

    String name = scanner.next();

    System.out.println("Frame " + i+" is sent"); 

    Socket s1;

        s1= new Socket(h,p+i);

        DataOutputStream d = new DataOutputStream(s1.getOutputStream());

        d.writeUTF(name);

        DataInputStream dd= new DataInputStream(s1.getInputStream());

        Integer sss1 = dd.read();

        System.out.println("Ack for :" + sss1 + " is  received");

        }

    }

    catch(Exception ex)

            {

                System.out.println("ERROR :"+ex);

            }

} 

}
"""
    c = """import java.io.*;
import java.net.*;

import java.util.*;

public class receiver {

    public static void main(String args[])

{

    String h="Serverhost";

    int q=5000;

    int i;

        try

        {         

        ServerSocket ss2;

            ss2 = new ServerSocket(8000);

            Socket s1 =ss2.accept();

        DataInputStream dd1= new DataInputStream(s1.getInputStream());

        Integer i1 =dd1.read();

        for(i=0;i<i1;i++)

        {

            ServerSocket ss1;

            ss1 = new ServerSocket(9000+i);

            Socket s =ss1.accept();

        DataInputStream dd= new DataInputStream(s.getInputStream());

        String sss1 = dd.readUTF();

            System.out.println(sss1);

            System.out.println("Frame "+ i+" received");

        DataOutputStream d1 = new DataOutputStream(s.getOutputStream());

        d1.write(i);

         System.out.println("ACK sent for "+ i); 

        }

        }

        catch(Exception ex)

        {

         System.out.println("Error"+ex);

                }

}

}
"""
    return s,c

def SlidingWindowProtocol_6():
    s = """import java.io.*;
import java.net.*;
public class slideserver
{
public static void main(String args[])throws IOException
{
byte msg[]=new byte[200];
ServerSocket ser=new ServerSocket(2000);
Socket s;
PrintStream pout;
DataInputStream in=new DataInputStream(System.in);
int start,end,l,j=0,i,ws=5,k=0;
String st,stl[]=new String[100];
System.out.println("Type\"Stop\"to exit");
s=ser.accept();
pout=new PrintStream(s.getOutputStream());
DataInputStream rin=new DataInputStream(s.getInputStream());
System.out.println("enter data to be send:");
while(true)
{
st=in.readLine();
l=st.length();
start=0;
end=10;
j=0;
if(st.equals("STOP"))
{
pout.println(st);
break;
}
if(l<10)
{stl[j++]=l+st;
}
else
{
for(i=l,j=0;i>0;i=i-10,j++)
{
stl[j]=(j+1)+st.substring(start,end);
start=end;
end=end+10;
if(end>l)
{
end=((start-10)+i);
}}
System.out.println("total number of packet"+j);
}
pout.println(j);
for(i=0;i<j;i++)
{
pout.println(stl[i]);
if((i+1)%ws==0)
{
System.out.println(rin.readLine());
}}
if(i%ws!=0)
{
System.out.println(rin.readLine());
System.out.println("enter next data to send");
}
}}}
"""
    c = """import java.io.*;
import java.net.*;
public class slideclient
{
           	public static void main(String args[])throws IOException
           	{
                	byte msg[]=new byte[200];
                	Socket s=new Socket(InetAddress.getLocalHost(),2000);
                	DataInputStream in=new DataInputStream(s.getInputStream());
                	DataInputStream ain=new DataInputStream(System.in);
                	PrintStream p=new PrintStream(s.getOutputStream());
                	char ch;
                	int i=0,ws=5;
                	while(true)
                	{
                          	String str,astr;
                          	int j=0;
                                    i=0;
                          	str=in.readLine();
                          	if(str.equals("STOP"))
                                    	System.exit(0);
                          	j=Integer.parseInt(str);
                          	for(i=0;i<j;i++)
                          	{
                                    	str=in.readLine();
                                    	System.out.println(str);
                                    	if((i+1)%ws==0)
                                    	{
                                              	System.out.println("Give the ack by press\"Enter\"key");
                                              	astr=ain.readLine();
                                              	p.println((i+1)+"ack");
                                    	}}
                          	if((i%ws)!=0)
                          	{
                                    	System.out.println("Give the ack by press\"Enter\"key");
                                    	astr=ain.readLine();
                                    	p.println(i+"ack");}
                          	System.out.println("All data are recieved and ack");
                	}}}
"""
    return s,c


def ARPprotocols_7():
    s = """import java.io.*; 
import java.net.*; 
import java.util.*;
 class Serverarp
{
public static void main(String args[])
{
try{
ServerSocket obj=new ServerSocket(139); 
Socket obj1=obj.accept();
while(true)
{
DataInputStream din=new DataInputStream(obj1.getInputStream()); 
DataOutputStream dout=new DataOutputStream(obj1.getOutputStream());
 String str=din.readLine();
String ip[]={"165.165.80.80","165.165.79.1"};
String mac[]={"6A:08:AA:C2","8A:BC:E3:FA"};
for(int i=0;i<ip.length;i++)
{
 if(str.equals(ip[i]))
{
dout.writeBytes(mac[i]+'\n'); break;
}
}
obj.close();
}
}
catch(Exception e)
{
System.out.println(e);
} } }"""
    c = """import java.io.*;
 import java.net.*;
 import java.util.*;
 class Clientarp
{
public static void main(String args[])
{
try{
BufferedReader in=new BufferedReader(new InputStreamReader(System.in)); 
Socket clsct=new Socket("127.0.0.1",139);
DataInputStream din=new DataInputStream(clsct.getInputStream());
 DataOutputStream dout=new DataOutputStream(clsct.getOutputStream()); System.out.println("Enter the Logical address(IP):");
String	str1=in.readLine(); dout.writeBytes(str1+'\n'); 
String str=din.readLine();
System.out.println("The Physical Address is: "+str); 
clsct.close();}
catch (Exception e){
System.out.println(e);
}}}
"""
    return s,c

def RARPusingUDP_8():
    s = """import java.io.*;
 import java.net.*;
 import java.util.*; 
class Serverrarp
{
public static void main(String args[]){
try{
DatagramSocket server=new DatagramSocket(1309);
 while(true)
{
byte[] sendbyte=new byte[1024]; 
byte[] receivebyte=new byte[1024];
DatagramPacket receiver=new DatagramPacket(receivebyte,receivebyte.length); server.receive(receiver);
String str=new String(receiver.getData());
 String s=str.trim();
InetAddress addr=receiver.getAddress();
 int port=receiver.getPort();
String ip[]={"165.165.80.80","165.165.79.1"};
String mac[]={"6A:08:AA:C2","8A:BC:E3:FA"};
for(int i=0;i<ip.length;i++)
{
if(s.equals(mac[i]))
{
sendbyte=ip[i].getBytes();
DatagramPacket sender=new DatagramPacket(sendbyte,sendbyte.length,addr,port);
server.send(sender); break;
}
}
break;
}
}
catch(Exception e)
{
System.out.println(e);
}
}
}

"""
    c = """import java.io.*;
 import java.net.*;
 import java.util.*; 
class Clientrarp{
public static void main(String args[]){
try{
DatagramSocket client=new DatagramSocket(); 
InetAddress addr=InetAddress.getByName("127.0.0.1"); 
byte[] sendbyte=new byte[1024];
byte[] receivebyte=new byte[1024];
BufferedReader in=new BufferedReader(new InputStreamReader(System.in)); System.out.println("Enter the Physical address (MAC):");
String str=in.readLine();
 sendbyte=str.getBytes();
DatagramPacket sender=new DatagramPacket(sendbyte,sendbyte.length,addr,1309);
client.send(sender);
DatagramPacket receiver=new DatagramPacket(receivebyte,receivebyte.length);
client.receive(receiver);
String s=new String(receiver.getData());
 System.out.println("The Logical Address is(IP): "+s.trim());
 client.close();
}
catch(Exception e)
{
System.out.println(e);
}}}"""
    return s,c

def echoCS_TCP_9():
    s = """import java.net.*;
import java.io.*;
public class EServer
{
public static void main(String args[])
{
ServerSocket s=null;
String line;
DataInputStream is;
PrintStream ps;
Socket c=null;
try
{
s=new ServerSocket(9000);
}
catch(IOException e)
{
    System.out.println(e);
}
try
{
c=s.accept();
is=new DataInputStream(c.getInputStream());
ps=new PrintStream(c.getOutputStream());
while(true)
{
line=is.readLine();
ps.println(line);
}
}
catch(IOException e)
{
System.out.println(e);
}
}
}"""
    c = """import java.net.*;
import java.io.*;
public class EClient
{
public static void main(String arg[])
{
Socket c=null;
String line;
DataInputStream is,is1;
PrintStream os;
try
{
InetAddress ia = InetAddress.getLocalHost();
c=new Socket(ia,9000);
}
catch(IOException e)
{
    System.out.println(e);
}
try
{
os=new PrintStream(c.getOutputStream());
is=new DataInputStream(System.in);
is1=new DataInputStream(c.getInputStream());
while(true)
{
System.out.println("Client:");
line=is.readLine();
os.println(line);
System.out.println("Server:" + is1.readLine());
 
}}
catch(IOException e)
{
System.out.println("Socket Closed!");
 }
} }

"""
    return s,c

def CS_UDP_10():
    s = """import java.io.*;
import java.net.*;
class UDPserver
{
public static DatagramSocket ds;
public static byte buffer[]=new byte[1024];
public static int clientport=789,serverport=790;
public static void main(String args[])throws Exception
{
ds=new DatagramSocket(clientport);
System.out.println("press ctrl+c to quit the program");
BufferedReader dis=new BufferedReader(new InputStreamReader(System.in));
InetAddress ia=InetAddress.getLocalHost();
while(true)
{
DatagramPacket p=new DatagramPacket(buffer,buffer.length);
ds.receive(p);
String psx=new String(p.getData(),0,p.getLength());
System.out.println("Client:" + psx); System.out.println("Server:");
String str=dis.readLine();
if(str.equals("end"))
break;
buffer=str.getBytes();
ds.send(new DatagramPacket(buffer,str.length(),ia,serverport));
}}}
"""
    c = """import java .io.*;
import java.net.*;
class UDPclient{
public static DatagramSocket ds;
public static int clientport=789,serverport=790;
public static void main(String args[])throws Exception
{ byte buffer[]=new byte[1024];
ds=new DatagramSocket(serverport);
BufferedReader dis=new BufferedReader(new InputStreamReader(System.in));
System.out.println("server waiting");
InetAddress ia=InetAddress.getLocalHost();
while(true)
{ System.out.println("Client:");
String str=dis.readLine();
if(str.equals("end"))
break;
buffer=str.getBytes();
ds.send(new DatagramPacket(buffer,str.length(),ia,clientport));
DatagramPacket p=new DatagramPacket(buffer,buffer.length);
ds.receive(p);
String psx=new String(p.getData(),0,p.getLength());
System.out.println("Server:" + psx);
}}}
"""
    return s,c
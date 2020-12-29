package admin;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;

public class TestServer {
	private byte[] buffer = new byte[1024];
	public final void send(final String host, final int port, final byte[] bytes) {
		DatagramSocket ds = null;
		DatagramPacket dp = null;
		try {
			ds = new DatagramSocket();
			dp = new DatagramPacket(bytes, bytes.length, InetAddress
					.getByName(host), port);
			ds.send(dp);
			ds.close();
			ds = null;
			dp = null;
		} catch (Exception e) {
			try {
				if (ds != null) {
					ds.close();
					ds = null;
				}
			} catch (Exception eee) {
			}
			try {
				if (dp != null) {
					dp = null;
				}
			} catch (Exception ee3e) {
			}
		}
	}
	
	public final void receive(final String lhost, final int lport) {
		DatagramSocket ds = null;
		DatagramPacket dp = null;
		try {
			ds = new DatagramSocket(4444);
			dp = new DatagramPacket(buffer, buffer.length);
			ds.receive(dp);
			String info = new String(dp.getData(), 0, dp.getLength());
			System.out.println("收到信息 客户端来的 " + info);
			ds.close();
			ds = null;
			dp = null;
		} catch (IOException e) {
			try {
				if (ds != null) {
					ds.close();
					ds = null;
				}
			} catch (Exception eee) {
			}
			try {
				if (dp != null) {
					dp = null;
				}
			} catch (Exception ee3e) {
			}
		}

	}
	
	 public static void main(String[] args) throws Exception {  
	        TestServer server = new TestServer();  
	        String serverHost = "127.0.0.1";  
	        int serverPort = 4444;  
	        for(int i=0;i<=10;i++){
	        	//发送到 local  3333
	        	server.send(serverHost, serverPort, ("你好，客户端!").getBytes());  
	        	//从指定端口接受
	        	server.receive(serverHost, 4444);  
	            
	        }
	    }  
}

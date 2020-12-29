package admin;
import java.io.IOException;  
import java.net.DatagramPacket;  
import java.net.DatagramSocket;  
import java.net.InetAddress;  
import java.net.InetSocketAddress;  
import java.net.SocketException;   
public class UdpServerSocket {  
    private byte[] buffer = new byte[1024];  
      
    private DatagramSocket ds = null;  
  
    private DatagramPacket packet = null;  
  
    private InetSocketAddress socketAddress = null;  
  
    private String orgIp;  
  
    public UdpServerSocket(String host, int port) throws Exception {  
        socketAddress = new InetSocketAddress(host, port);  
        ds = new DatagramSocket(socketAddress);  
        System.out.println("服务器已启动!");  
    }  
      
    public final String getOrgIp() {  
        return orgIp;  
    }  
    public final void setSoTimeout(int timeout) throws Exception {  
        ds.setSoTimeout(timeout);  
    }  
    public final int getSoTimeout() throws Exception {  
        return ds.getSoTimeout();  
    }  
  
    /** 
     * 绑定监听地址和端口. 
     * @param host 主机IP 
     * @param port 端口 
     * @throws SocketException 
     */  
    public final void bind(String host, int port) throws SocketException {  
        socketAddress = new InetSocketAddress(host, port);  
        ds = new DatagramSocket(socketAddress);  
    }  
    public final void setLength(int bufsize) {  
        packet.setLength(bufsize);  
    }  
  
    /** 
     * 获得发送回应的IP地址. 
     * @return 返回回应的IP地址 
     */  
    public final InetAddress getResponseAddress() {  
        return packet.getAddress();  
    }  
  
    /** 
     * 获得回应的主机的端口. 
     * @return 返回回应的主机的端口. 
     * @author <a href="mailto:xiexingxing1121@126.com">AmigoXie</a> 
     * Creation date: 2007-8-16 - 下午10:48:56 
     */  
    public final int getResponsePort() {  
        return packet.getPort();  
    }  
  
    /** 
     * 关闭udp监听口. 
     * @author <a href="mailto:xiexingxing1121@126.com">AmigoXie</a> 
     * Creation date: 2007-8-16 - 下午10:49:23 
     */  
    public final void close() {  
        try {  
            ds.close();  
        } catch (Exception ex) {  
            ex.printStackTrace();  
        }  
    }  
  
    /** 
     * 测试方法. 
     * @param args 
     * @throws Exception 
     * @author <a href="mailto:xiexingxing1121@126.com">AmigoXie</a> 
     * Creation date: 2007-8-16 - 下午10:49:50 
     */  
    public final void response(String info) throws IOException {  
        System.out.println("客户端地址 : " + packet.getAddress().getHostAddress()  
                + ",端口：" + 4444);  
        DatagramPacket dp = new DatagramPacket(buffer, buffer.length, packet  
                .getAddress(), 4444);  
        dp.setData(info.getBytes());  
        ds.send(dp);  
    }  
    public final String receive() throws IOException {  
        packet = new DatagramPacket(buffer, buffer.length);  
        ds.receive(packet);  
        orgIp = packet.getAddress().getHostAddress();  
        String info = new String(packet.getData(), 0, packet.getLength());  
        System.out.println("接收信息：" + info);  
        return info;  
    }  
    public static void main(String[] args) throws Exception {  
        String serverHost = "127.0.0.1";  
        int serverPort = 3333;  
        UdpServerSocket udpServerSocket = new UdpServerSocket(serverHost, serverPort);  
        while (true) {  
            udpServerSocket.receive();  
            udpServerSocket.response("你好,客户端!");  
              
        }  
    }  
}  
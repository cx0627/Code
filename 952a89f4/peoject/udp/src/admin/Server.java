package admin;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.regex.Pattern;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JTextField;

public class Server extends JFrame implements ActionListener {

	private JPanel pane;
	public JTextField ipName;
	public JLabel ip;
	public JLabel textRecievePort;
	public JTextField textRecievePortName;
	public JLabel textSendPort;
	public JTextField textSendPortName;
	public JLabel talk;
	public JTextField talkName;
	public JButton button;
	public static boolean showTag=false;
	public UdpServer talkServer;
	public Server() {
		this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		pane = new JPanel(); // 创建面板
		textRecievePort = new JLabel("输入端口号：");
		textRecievePort.setBounds(120, 110, 100, 100);
		textRecievePortName = new JTextField(11);
		textRecievePortName.setText("11");
		textRecievePortName.setBounds(220, 110, 100, 100);
		ip = new JLabel("对方的IP地址:");
		ip.setBounds(120, 310, 100, 100);
		ipName = new JTextField(11);
		ipName.setBounds(220, 310, 100, 100);
		ipName.setText("localhost");
		
		textSendPort = new JLabel("输出端口号：");
		textSendPort.setBounds(120, 410, 100, 100);
		textSendPortName = new JTextField(11);
		textSendPortName.setText("22");
		textSendPortName.setBounds(220, 410, 100, 100);
		
		talk = new JLabel("你的昵称是：");
		talk.setBounds(120, 510, 100, 100);
		talkName = new JTextField(11);
		talkName.setText(" ");
		talkName.setBounds(220, 510, 100, 100);
		
		button = new JButton("进入");
		button.setBounds(200, 350, 100, 100);
		pane.add(textRecievePort);
		pane.add(textRecievePortName);
		pane.add(ip);
		pane.add(ipName);	
		pane.add(textSendPort);
		pane.add(textSendPortName);
		pane.add(talk);
		pane.add(talkName);
		pane.add(button);
		button.addActionListener(this);
		/*
		 * pane.add(btn2); pane.add(btn3); // 将组件添加到面板中
		 */
		this.add(pane); // 将面板添加到窗体
		this.setVisible(true);
		this.setBounds(350, 100, 280, 400);
		this.setTitle("我的服务器启动界面");
		
		//添加关闭窗口事件
		this.addWindowListener(new WindowAdapter(){
    		public void windowClosing(WindowEvent event)
    		{
				System.exit(0);
    		}
		});
		
	}
	public void actionPerformed(ActionEvent g){   
		 if(g.getSource()==button){//进入
			 int errTag=0;
			 int recieveTextPort =0;
			 int sendTextPort=0;
			 DatagramSocket ds = null;
			 DatagramPacket dp = null;
			 String ip="";
				try {
					
					ip = ipName.getText().trim();
					try{
						recieveTextPort=Integer.parseInt(textRecievePortName.getText().trim());
					}catch(Exception e){

						JOptionPane.showMessageDialog(this,"您输入的输入端口号有误!","错误提示",JOptionPane.ERROR_MESSAGE);
						errTag=1;
					}
					
					
					if(errTag==0){
						if((ip.equals("localhost") || ip.equals("127.0.0.1"))){
							errTag=0;
						}else if(!Pattern.compile("\\d{0,3}\\.\\d{0,3}\\.\\d{0,3}\\.\\d{0,3}").matcher(ip).matches()){
							JOptionPane.showMessageDialog(this,"您输入的对方ip地址有误!","错误提示",JOptionPane.ERROR_MESSAGE);
							errTag=1;
							//int i=JOptionPane.showConfirmDialog(null,"保存到:"+getTitle(),"保存",JOptionPane.YES_NO_OPTION);
						}
						if(errTag==0){//目标文本端口
							try{
								System.out.println(textSendPortName.getText().trim());
								sendTextPort=Integer.parseInt(textSendPortName.getText().trim());
							}catch(Exception e){
								JOptionPane.showMessageDialog(this,"您输入的输出端口号有误!","错误提示",JOptionPane.ERROR_MESSAGE);
								errTag=1;
							}
							
						}
						if(errTag==0){
							String name=talkName.getText().trim();
							if(name==null || name.equals("")){
								JOptionPane.showMessageDialog(this,"您的会话昵称不能为空!","错误提示",JOptionPane.ERROR_MESSAGE);
								errTag=1;
							}
						}
						if(errTag==0){
							
								byte[] bytes="".getBytes();
								ds = new DatagramSocket();
								dp = new DatagramPacket(bytes, bytes.length, InetAddress
										.getByName(ip), sendTextPort);
								//ds.send(dp);
								ds.close(); 
								ds = null;
								dp = null;							
							this.setVisible(false);	
							this.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
							this.dispose();
							if(showTag==true){//表示显示
								this.talkServer.setNewIpPort(ip,sendTextPort,recieveTextPort,this,talkName.getText().trim());
								this.talkServer.setVisible(true);
								this.talkServer.area.setText("");
							}else{
								showTag=false;
								new UdpServer(sendTextPort,ip,recieveTextPort,this,talkName.getText().trim());	
							//	new TalkFrameServer(1,ip,sendTextPort,sendFilePort,recieveTextPort,recieceFilePort,this);					
								
							}
							
							
						}
					}
				} catch (Exception ee) {
					if(ds!=null){
						try{
							ds.close();
							ds=null;
						}catch (Exception e) {
						}
					}
					if(dp!=null){
						try{
							dp=null;
						}catch (Exception e) {
						}
					}
					int i=JOptionPane.showConfirmDialog(null,"ip："+ip+" port "+sendTextPort+" 上的客户端并没有启动，是否需要继续？","继续",JOptionPane.YES_NO_OPTION);
					if(i==1){
						
					}else{
						this.setVisible(false);	
						this.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
						this.dispose();
						if(showTag==true){//表示显示
							this.talkServer.setNewIpPort(ip,sendTextPort,recieveTextPort,this,talkName.getText().trim());
							this.talkServer.setVisible(true);
							this.talkServer.area.setText("");
							
						}else{
							showTag=false;
							new UdpServer(sendTextPort,ip,recieveTextPort,this,talkName.getText().trim());												
						}
					}
				}

			}

		}
	//显示窗口http://bbs.bccn.net/thread-118338-1-1.html
	//或者在while循环中使用sleep(time)方法造成阻塞，然后用interrupt（）中断
	public void setShowTag(boolean tag,UdpServer client){
		this.showTag=tag;
		this.talkServer=client;
	}
	
	public static void main(String[] args) {
		new Server();
	}
}

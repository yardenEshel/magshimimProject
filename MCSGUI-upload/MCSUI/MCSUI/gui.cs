using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Windows.Forms;

namespace MCSUI
{
    public partial class MCS : Form
    {
        IPEndPoint remoteEP;
        Socket sender;
        public MCS()
        {
            InitializeComponent();

            // Data buffer for incoming data.  
            byte[] bytes = new byte[1024];

            // Connect to a remote device.  
            // Establish the remote endpoint for the socket.  
            IPHostEntry ipHostInfo = Dns.GetHostEntry(Dns.GetHostName());
            IPAddress ipAddress = IPAddress.Parse("127.0.0.1");
            remoteEP = new IPEndPoint(ipAddress, 2345);

            // Create a TCP/IP  socket.  
            sender = new Socket(ipAddress.AddressFamily,
                SocketType.Stream, ProtocolType.Tcp);

            // Connect the socket to the remote endpoint. Catch any errors.  

            sender.Connect(remoteEP);
            Console.WriteLine("Socket connected to {0}",
                sender.RemoteEndPoint.ToString());
        }

        private void start_button_Click(object sender, EventArgs e) => Send_service("1");

        private void MCS_Load(object sender, EventArgs e)
        {

        }

        private void ErrMsg_Click(object sender, EventArgs e)
        {

        }
        private void StartClient(byte[] msg)
        {
            // Data buffer for incoming data.  
            byte[] bytes = new byte[1024];

            // Connect to a remote device.  
            try
            {

                Console.WriteLine("Socket connected to {0}",
                    sender.RemoteEndPoint.ToString());

                // Encode the data string into a byte array.  


                // Send the data through the socket.  
                int bytesSent = sender.Send(msg);

                // Receive the response from the remote device.  

                int bytesRec = sender.Receive(bytes);
                string response = (Encoding.ASCII.GetString(bytes, 0, bytesRec));
                if(response == "11")
                {
                    Form2 remoteDesktop = new Form2();
                    this.Hide();
                    remoteDesktop.Show();

                }
                Console.WriteLine("Echoed test = {0}", response);

            }
            catch (ArgumentNullException ane)
            {
                ErrMsg.Text = ("ArgumentNullException : {0}" + ane.ToString());
            }
            catch (SocketException se)
            {
                ErrMsg.Text = ("SocketException : {0}" + se.ToString());
            }
            catch (Exception e)
            {
                ErrMsg.Text = ("Unexpected exception :" + e.ToString());
            }
        }

        private int Send_service(String arg)
        {
            StartClient(Encoding.ASCII.GetBytes(arg));
            return 0;
        }

        

        private void stop_button_Click(object sender, EventArgs e)
        {
            Send_service("2");
        }
        private void cpu_button_Click(object sender, EventArgs e)
        {
            Send_service("3");
            this.Hide();
        }
    }


}

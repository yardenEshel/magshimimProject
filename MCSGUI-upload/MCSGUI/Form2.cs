using System;
using System.Drawing;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Windows.Forms;

namespace MCSUI
{
    [System.Runtime.InteropServices.Guid("5CA9E190-022C-4743-A215-1EE903E169C9")]

    public partial class Form2 : Form
    {
        Form1 b;
        public Form2(Form1 b1)
        {
            InitializeComponent();
            b = b1;
        }
        public static string client_ip;
        public static byte[] data = null;
        public static int NofP = 20;
        public static int padd = 6;
        public static int KeyPressed = -1;
        public static int click = -1;
        public static Point currentpoint = new Point(0, 0);
        public static void StartListening(Form2 a)
        {
            int recv;
            byte[] png;
            IPEndPoint ipep = new IPEndPoint(IPAddress.Any, 3456);

            Socket newsock = new Socket(AddressFamily.InterNetwork,
                            SocketType.Dgram, ProtocolType.Udp);

            newsock.Bind(ipep);
            Console.WriteLine("Waiting for a client...");

            IPEndPoint sender = new IPEndPoint(IPAddress.Any, 0);
            EndPoint Remote = (EndPoint)(sender);
            bool ip_flag = false;
            byte[] ip_string = new byte[18];
            string iip = "";
            while (true)
            {
                if (!ip_flag)
                {
                    try
                    {
                        while (iip == "")
                        {
                            recv = newsock.ReceiveFrom(ip_string, ref Remote);
                            iip = Encoding.ASCII.GetString(ip_string).Replace("\0", "");
                            iip = iip.Substring(0, iip.Length - 3);
                            Console.WriteLine(iip);
                            client_ip = IPAddress.Parse(iip).ToString();
                            Console.WriteLine(client_ip.ToString());
                        }
                        ip_flag = true;
                        Form4 loading = new Form4(newsock, Remote);
                        
                        loading.ShowDialog();
                        Console.WriteLine("ready to share");
                        a.Invoke(new MethodInvoker(a.Show));
                    }
                    catch (Exception e)
                    {

                    }
                }
                else
                {

                    try
                    {

                        byte[] data = new byte[padd];
                        recv = newsock.ReceiveFrom(data, ref Remote);
                        int png_PartLen = Int32.Parse(Encoding.ASCII.GetString(data));
                        png = new byte[png_PartLen * NofP];
                        for (int i = 0; i < NofP; i++)
                        {

                            data = new byte[png_PartLen];
                            recv = newsock.ReceiveFrom(data, ref Remote);
                            data.CopyTo(png, i * png_PartLen);
                        }
                        a.pictureBox1.Image = a.stringToImage(png);
                        a.pictureBox1.Refresh();

                    }
                    catch (Exception e)
                    {

                    }
                }
            }


        }
        public static void cursor_and_keyboard()
        {
            while (client_ip == "0.0.0.0" || client_ip == null)
            { System.Threading.Thread.Sleep(300); }
            Console.WriteLine("keyboard");
            //keyboard:
            UdpClient udpClient = new UdpClient(5678);
            udpClient.Connect(client_ip, 5678);
            int key = -1;
            int clicked = -1;
            string mx = null;
            string my = null;
            Byte[] sendBytes = new Byte[0];
            Byte[] sendBytes2;
            Byte[] sendBytes1;
            Point before = new Point(0, 0);
            while (true)
            {

                do
                {
                    key = KeyPressed;
                    clicked = click;
                    System.Threading.Thread.Sleep(1);


                    if (before != currentpoint)
                    {
                        before = currentpoint;
                        if (currentpoint.X > 0)
                        {
                            mx = "+";
                        }
                        else
                        {
                            mx = null;
                        }

                        if (currentpoint.Y > 0)
                        {
                            my = "+";
                        }
                        else
                        {
                            my = null;
                        }
                        if (sendBytes != Encoding.ASCII.GetBytes(mx + currentpoint.X.ToString("D4") + my + currentpoint.Y.ToString("D4")))
                        {
                            sendBytes1 = Encoding.ASCII.GetBytes("m");
                            udpClient.Send(sendBytes1, sendBytes1.Length);
                            sendBytes2 = Encoding.ASCII.GetBytes("m");
                            udpClient.Send(sendBytes2, sendBytes2.Length);

                            sendBytes = Encoding.ASCII.GetBytes(mx + currentpoint.X.ToString("D4") + my + currentpoint.Y.ToString("D4"));


                            udpClient.Send(sendBytes, sendBytes.Length);
                            Console.WriteLine(mx + currentpoint.X.ToString("D4") + my + currentpoint.Y.ToString("D4"));
                        }


                    }

                } while (key == -1 && clicked == -1);
                if (key != -1)
                {
                    sendBytes = Encoding.ASCII.GetBytes("k");
                    udpClient.Send(sendBytes, sendBytes.Length);
                    sendBytes = Encoding.ASCII.GetBytes(key.ToString("D4"));
                    udpClient.Send(sendBytes, sendBytes.Length);
                }
                if (click != -1)
                {

                    sendBytes = Encoding.ASCII.GetBytes("m");
                    udpClient.Send(sendBytes, sendBytes.Length);
                    sendBytes = Encoding.ASCII.GetBytes("c");
                    udpClient.Send(sendBytes, sendBytes.Length);
                    sendBytes = Encoding.ASCII.GetBytes(click.ToString());
                    udpClient.Send(sendBytes, sendBytes.Length);
                }
                clicked = -1;
                click = -1;
                KeyPressed = -1;
            }




        }
        public static int Main1(Form2 a)
        {
            Thread listen = new Thread(() => StartListening(a));
            listen.Start();
            return 0;
        }

        public Bitmap stringToImage(byte[] inputString)
        {

            using (MemoryStream ms = new MemoryStream(inputString))
            {
                return new Bitmap(ms);
            }
        }

        private void Form2_Shown(object sender, EventArgs e)
        {
            
            FormBorderStyle = FormBorderStyle.None;
            WindowState = FormWindowState.Maximized;
            var childref = new Thread(cursor_and_keyboard);
            childref.Start();
            Main1(this);
        }

        private void Form2_Load(object sender, EventArgs e)
        {

        }

        private void Form2_KeyPress(object sender, KeyPressEventArgs e)
        {
            KeyPressed = e.KeyChar;
        }

        private void Form2_MouseClick(object sender, MouseEventArgs e)
        {
            switch (e.Button)
            {

                case MouseButtons.Left:

                    click = 1;
                    break;

                case MouseButtons.Right:

                    click = 2;
                    break;
                case MouseButtons.Middle:

                    click = 0;
                    break;
                default:
                    click = -1;
                    break;
            }

        }

        private void Form2_MouseUp(object sender, MouseEventArgs e)
        {
            if (click == 3 || click == -1)
            {
                click = -1;
            }
            else
            {
                System.Threading.Thread.Sleep(50);
                click = 3;
            }


        }

        private void mousemove(object sender, MouseEventArgs e)
        {

            currentpoint = new Point(MousePosition.X, MousePosition.Y);
        }

        


    }

}

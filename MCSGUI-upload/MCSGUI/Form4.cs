using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net;
using System.Net.Sockets;
using System.Windows.Forms;
using System.Threading;
using System.Windows.Forms.DataVisualization.Charting;

namespace MCSUI
{
    public partial class Form4 : Form
    {

        byte[] ip_string = new byte[18];
        string iip = "";
        int perc = 0;
        public Form4(Socket sender, EndPoint remote1)
        {
            InitializeComponent();
            this.CenterToScreen();
            table = sender;
            remote = remote1;
            pictureBox1.Enabled = true;
            loadingLabal.Visible = true;
            loadingLabal.Parent = pictureBox1;
            loadingLabal.BackColor = Color.Transparent;
            
            this.loadingLabal.BringToFront();

        }
        public Socket table;
        public EndPoint remote;
        private void label1_Click(object sender, EventArgs e)
        {

        }

        private void Form4_Load(object sender, EventArgs e)
        {

        }
        private void percentage(Socket table, EndPoint remote, Form4 a)
        {
            while (perc != 100)
            {
                table.ReceiveFrom(ip_string, ref remote);
                iip = Encoding.ASCII.GetString(ip_string).Replace("\0", "");
                perc = Int32.Parse(iip.Substring(iip.Length - 3, 3));
                a.loadingLabal.Invoke(new Action(() => a.loadingLabal.Text = "  "+perc.ToString()+"%"));
                a.loadingLabal.Invoke(new Action(() => a.loadingLabal.Refresh()));

            }
            a.Invoke(new Action(() => a.Close()));
        }
        private void Form4_Shown(object sender, EventArgs e)
        {
            Thread listen = new Thread(() => percentage(table,remote, this));
            listen.Start();
        }

        private void rectangleShape2_Click(object sender, EventArgs e)
        {

        }

        private void pictureBox1_Click(object sender, EventArgs e)
        {

        }
    }
}

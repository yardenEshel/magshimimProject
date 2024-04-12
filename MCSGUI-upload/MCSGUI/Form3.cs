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
    public partial class Form3 : Form
    {
        bool stop = false;
        List<int> cpues;
        public Form3(Socket sender, IPEndPoint remoteEP)
        {
            InitializeComponent();
            table = sender;
            remote = remoteEP; 

        }
        public Socket table;
        public IPEndPoint remote;
        private void Form3_Shown(object sender, EventArgs e)
        {
            var childref = new Thread(mania);
            childref.Start();
            
        }
        private void Form3_Load(object sender, EventArgs e)
        {
            
            chart1.Series.Clear();
            chart1.BackColor = SystemColors.ActiveCaption;
            chart1.ChartAreas[0].AxisX.MajorGrid.LineWidth = 0;
            chart1.ChartAreas[0].AxisY.MajorGrid.LineWidth = 0;
            chart1.ChartAreas[0].BackColor = SystemColors.ActiveCaption;
        }
        private void mania()
        {
            int counter = 1;
            cpues = new List<int>();
            do
            {
                // Data buffer for incoming data.  
                byte[] bytes = new byte[1024];

                // Connect to a remote device.  

                Console.WriteLine("Socket connected to {0}",
                table.RemoteEndPoint.ToString());

                // Encode the data string into a byte array.  


                // Send the data through the socket.  
                int bytesSent = table.Send(Encoding.UTF8.GetBytes("3"));

                // Receive the response from the remote device.  

                int bytesRec = table.Receive(bytes);
                string response = (Encoding.ASCII.GetString(bytes, 0, bytesRec));
                Console.WriteLine("the CPU is {0}", response);

                cpues.Clear();
                while (response.Length != 0)
                {
                    Console.WriteLine("computer no"+counter.ToString());
                    int namelength = Int32.Parse(response.Substring(0, 2));
                    string series = response.Substring(2, namelength);
                    Console.WriteLine(series);
                    string CPU = response.Substring(2 + namelength, 2);
                    cpues.Add(Int32.Parse(CPU));
                    Console.WriteLine(CPU);
                    response = response.Substring(4 + namelength);
                    Console.WriteLine(response);
                    if (chart1.Series.IndexOf(series) != -1)
                    {
                        // Series Exists

                    }
                    else
                    {
                        // Series Does Not Exist

                        chart1.Invoke(new Action(() => chart1.Series.Add(series)));
                        chart1.Invoke(new Action(() => chart1.Series[series].ChartType = SeriesChartType.Line));
                        chart1.Invoke(new Action(() => chart1.Series[series].BorderWidth = 5));

                    }
                    
                    chart1.Invoke(new Action(() => chart1.Series[series].Points.AddXY(counter, Int32.Parse(CPU))));
                   
                    
                }
                if (cpues.Count > 1)
                {
                    if (chart1.Series.IndexOf("avg CPU %") != -1)
                    {
                        // Series Exists

                    }
                    else
                    {
                        chart1.Invoke(new Action(() => chart1.Series.Add("avg CPU %")));
                        chart1.Invoke(new Action(() => chart1.Series["avg CPU %"].ChartType = SeriesChartType.Line));
                        

                    }
                    chart1.Invoke(new Action(() => chart1.Series["avg CPU %"].Points.AddXY(counter, Int32.Parse(Math.Round(cpues.Average()).ToString()))));
                    Console.WriteLine("next!");
                    
                    
                }
                System.Threading.Thread.Sleep(1000);
                counter++;
            }
            while (stop == false);
        }

        private void button1_Click(object sender, EventArgs e)
        {
            stop = true;
            this.Close();
        }

        private void chart1_Click(object sender, EventArgs e)
        {

        }
    }
}

namespace MCSUI
{
    partial class MCS
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MCS));
            this.ErrMsg = new System.Windows.Forms.Label();
            this.cpu_button = new System.Windows.Forms.PictureBox();
            this.stop_button = new System.Windows.Forms.PictureBox();
            this.start_button = new System.Windows.Forms.PictureBox();
            ((System.ComponentModel.ISupportInitialize)(this.cpu_button)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.stop_button)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.start_button)).BeginInit();
            this.SuspendLayout();
            // 
            // ErrMsg
            // 
            this.ErrMsg.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.ErrMsg.AutoSize = true;
            this.ErrMsg.Font = new System.Drawing.Font("Microsoft Sans Serif", 14F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.ErrMsg.Location = new System.Drawing.Point(50, 350);
            this.ErrMsg.Name = "ErrMsg";
            this.ErrMsg.Size = new System.Drawing.Size(28, 27);
            this.ErrMsg.TabIndex = 1;
            this.ErrMsg.Text = "__";
            this.ErrMsg.UseCompatibleTextRendering = true;
            this.ErrMsg.Click += new System.EventHandler(this.ErrMsg_Click);
            // 
            // cpu_button
            // 
            this.cpu_button.Image = global::MCSUI.Properties.Resources.CPI;
            this.cpu_button.Location = new System.Drawing.Point(624, 122);
            this.cpu_button.Name = "cpu_button";
            this.cpu_button.Size = new System.Drawing.Size(129, 122);
            this.cpu_button.SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom;
            this.cpu_button.TabIndex = 3;
            this.cpu_button.TabStop = false;
            this.cpu_button.Click += new System.EventHandler(this.cpu_button_Click);
            // 
            // stop_button
            // 
            this.stop_button.Image = global::MCSUI.Properties.Resources.stop_button;
            this.stop_button.Location = new System.Drawing.Point(41, 129);
            this.stop_button.Name = "stop_button";
            this.stop_button.Size = new System.Drawing.Size(123, 109);
            this.stop_button.SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom;
            this.stop_button.TabIndex = 2;
            this.stop_button.TabStop = false;
            this.stop_button.Click += new System.EventHandler(this.stop_button_Click);
            // 
            // start_button
            // 
            this.start_button.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.start_button.Image = global::MCSUI.Properties.Resources.start_button;
            this.start_button.Location = new System.Drawing.Point(230, 38);
            this.start_button.Margin = new System.Windows.Forms.Padding(100);
            this.start_button.Name = "start_button";
            this.start_button.Size = new System.Drawing.Size(331, 300);
            this.start_button.SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom;
            this.start_button.TabIndex = 0;
            this.start_button.TabStop = false;
            this.start_button.Click += new System.EventHandler(this.start_button_Click);
            // 
            // MCS
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = System.Drawing.SystemColors.ActiveCaption;
            this.ClientSize = new System.Drawing.Size(784, 461);
            this.Controls.Add(this.cpu_button);
            this.Controls.Add(this.stop_button);
            this.Controls.Add(this.ErrMsg);
            this.Controls.Add(this.start_button);
            this.ForeColor = System.Drawing.SystemColors.ActiveCaptionText;
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.Name = "MCS";
            this.Text = "MCS";
            this.Load += new System.EventHandler(this.MCS_Load);
            ((System.ComponentModel.ISupportInitialize)(this.cpu_button)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.stop_button)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.start_button)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.PictureBox start_button;
        private System.Windows.Forms.Label ErrMsg;
        private System.Windows.Forms.PictureBox stop_button;
        private System.Windows.Forms.PictureBox cpu_button;
    }
}


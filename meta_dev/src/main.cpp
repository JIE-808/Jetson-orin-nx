#include"rclcpp/rclcpp.hpp"
#include"sys/socket.h"
#include "netinet/in.h"
#include <arpa/inet.h>
#include "unistd.h"
#include "interfaces/msg/meta_key.hpp"
#include <fcntl.h>

class UdpServerNode:public rclcpp::Node
{
    private:
        rclcpp::Publisher<interfaces::msg::MetaKey>::SharedPtr pub_meta;
        std::thread udp_thread;
        unsigned char crc_table[256];
        struct HandData {
            uint8_t  addr;      // 0xf1
            uint8_t  func;      // 1
            int8_t  a;
            int8_t  b;
            int8_t  sk;
            int8_t  grab;
            int8_t  sk_x;
            int8_t  sk_y;
            int32_t  x;
            int32_t  y;
            int32_t  z;
            int32_t  xr;
            int32_t  yr;
            int32_t  zr;
            int32_t  wr;
        };
        HandData hand_data;
        std::string meta_ip="";
        const int meta_port=6666;
        const int robot_port = 9999;
        const int udp_buf_len=256;
        unsigned char udp_buf[256];
    public:
        UdpServerNode():Node("meta_dev_node"){
            pub_meta=create_publisher<interfaces::msg::MetaKey>("/meta_key",10);
            init_crc8();
            declare_parameter("meta_ip",std::string(""));
            meta_ip=get_parameter("meta_ip").as_string();
        }
        void init(){
            int ret=login_meta(1);
            if(ret==1){
                udp_thread=std::thread([this](){
                    struct sockaddr_in server_addr,client_addr;
                    socklen_t client_len = sizeof(client_addr);
                    int sockfd;
                    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
                        printf("UDP socket creation failed");
                        return;
                    }
                    int flags = fcntl(sockfd, F_GETFL, 0);
                    fcntl(sockfd, F_SETFL, flags | SOCK_NONBLOCK);
                    // 配置服务器地址
                    memset(&server_addr, 0, sizeof(server_addr));
                    server_addr.sin_family = AF_INET;
                    server_addr.sin_addr.s_addr = INADDR_ANY;
                    server_addr.sin_port = htons(robot_port);

                    // 绑定端口
                    if (bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
                        printf("Bind failed on port %d", robot_port);
                        close(sockfd);
                        return;
                    }

                    std::cout<<"UDP listener bound to port:"<< robot_port<<std::endl;
                    while (rclcpp::ok()) {
                        //std::cout<<"start recv..."<<std::endl;
                        ssize_t ret = recvfrom(sockfd, udp_buf, udp_buf_len, 0,
                                                        (struct sockaddr *)&client_addr, &client_len);
                        if (ret > 0) {
                        /*
                            std::cout<<"udp recv:"<<std::endl;
                            for(int i=0;i<ret;i++){
                                std::cout<<std::hex<<(unsigned int)udp_buf[i]<<",";
                            }
                            std::cout<<std::endl;
                        */
                            unsigned char crc=calc_crc8(udp_buf,ret-1);
                            if(udp_buf[ret-1]!=crc)
                                std::cout<<"crc:"<<std::hex<<(unsigned int)crc<<(unsigned int)udp_buf[ret-1]<<std::endl;
                            hand_data.addr=udp_buf[0];
                            hand_data.func=udp_buf[1];
                            hand_data.a=udp_buf[2];
                            hand_data.b=udp_buf[3];
                            hand_data.sk=udp_buf[4];
                            hand_data.grab=udp_buf[5];
                            hand_data.sk_x=udp_buf[6];
                            hand_data.sk_y=udp_buf[7];
                            hand_data.x=udp_buf[11]<<24|udp_buf[10]<<16|udp_buf[9]<<8|udp_buf[8];
                            hand_data.y=udp_buf[15]<<24|udp_buf[14]<<16|udp_buf[13]<<8|udp_buf[12];
                            hand_data.z=udp_buf[19]<<24|udp_buf[18]<<16|udp_buf[17]<<8|udp_buf[16];
                            hand_data.xr=udp_buf[23]<<24|udp_buf[22]<<16|udp_buf[21]<<8|udp_buf[20];
                            hand_data.yr=udp_buf[27]<<24|udp_buf[26]<<16|udp_buf[25]<<8|udp_buf[24];
                            hand_data.zr=udp_buf[31]<<24|udp_buf[30]<<16|udp_buf[29]<<8|udp_buf[28];
                            hand_data.wr=udp_buf[35]<<24|udp_buf[34]<<16|udp_buf[33]<<8|udp_buf[32];
                            /*
                            std::cout<<"hand:"<<std::dec<<(int)hand_data.a<<","<<(int)hand_data.b<<","<<(int)hand_data.sk<<","<<(int)hand_data.grab<<","
                                    <<(int)hand_data.sk_x<<","<<(int)hand_data.sk_y<<","<<(int)hand_data.x<<","<<(int)hand_data.y<<","<<(int)hand_data.z<<","
                                    <<(int)hand_data.xr<<","<<(int)hand_data.yr<<","<<(int)hand_data.zr<<","<<(int)hand_data.wr<<std::endl;
                            */
                            interfaces::msg::MetaKey metaKey;
                            metaKey.source="quest3";
                            if(udp_buf[0]==0xf0)
                                metaKey.type="right";
                            else if(udp_buf[0]==0xf1)
                                metaKey.type="left";
                            metaKey.a=hand_data.a;
                            metaKey.b=hand_data.b;
                            metaKey.sk=hand_data.sk;
                            metaKey.trigger=hand_data.grab;
                            metaKey.sk_x=hand_data.sk_x;
                            metaKey.sk_y=hand_data.sk_y;
                            metaKey.pose.position.x=hand_data.x/10000.0f;
                            metaKey.pose.position.y=hand_data.y/10000.0f;
                            metaKey.pose.position.z=hand_data.z/10000.0f;

                            metaKey.pose.orientation.x=hand_data.xr/10000.0f;
                            metaKey.pose.orientation.y=hand_data.yr/10000.0f;
                            metaKey.pose.orientation.z=hand_data.zr/10000.0f;
                            metaKey.pose.orientation.w=hand_data.wr/10000.0f;
                            this->pub_meta->publish(metaKey);
                        } else if (ret < 0) {
                            if (errno == EAGAIN || errno == EWOULDBLOCK ) {
                                std::this_thread::sleep_for(std::chrono::milliseconds(10));
                                continue;
                            }
                            std::cout<<"recvfrom error:"<<std::endl;
                            break;
                        }
                    }
                    close(sockfd);
                    std::cout<<"UDP listener stopped."<<std::endl;
                });
            }else{
                std::cout<<"login fail app exit!"<<std::endl;
                rclcpp::shutdown();
            }
        }
    
    void init_crc8(){
        const unsigned char poly = 0x07;
        for (int i = 0; i < 256; i++)
        {
            unsigned char crc = (unsigned char)i;
            for (int j = 0; j < 8; j++)
            {
                if ((crc & 0x80) != 0)
                    crc = (unsigned char)((crc << 1) ^ poly);
                else
                    crc <<= 1;
            }
            crc_table[i] = crc;
        }
    }
    unsigned char calc_crc8(const unsigned char *data, int len){
        unsigned char crc = 0x00;
        for(int i=0;i<len;i++)
        {
            unsigned char b=data[i];
            crc = crc_table[(crc ^ b) & 0xFF];
        }
        return crc; 
    }
    int login_meta(int type){
        
        struct sockaddr_in server_addr;
        udp_buf[0]=0xb0;
        udp_buf[1]=type;//1--login,0--logout
        udp_buf[2]=100;//发送间隔ms
        udp_buf[3]=calc_crc8(udp_buf,3);
        int sockfd;
        if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
            printf("UDP socket creation failed");
            return 0;
        }
        //int flags = fcntl(sockfd, F_GETFL, 0);
        //fcntl(sockfd, F_SETFL, flags | SOCK_NONBLOCK);
        memset(&server_addr, 0, sizeof(server_addr));
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(meta_port);
        server_addr.sin_addr.s_addr=inet_addr(meta_ip.c_str());

        ssize_t send_len = sendto(sockfd, udp_buf, 4, 0,(const struct sockaddr *)&server_addr, sizeof(server_addr));
        if (send_len < 0) {
            perror("sendto failed");
            close(sockfd);
            return 0;
        }
        struct timeval timeout;
        timeout.tv_sec = 5;
        timeout.tv_usec = 0;
        if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) < 0) {
            perror("setsockopt failed");
            close(sockfd);
            return 0;
        }
        socklen_t addr_len = sizeof(server_addr);
        int n = recvfrom(sockfd, udp_buf, udp_buf_len, 0,(struct sockaddr *)&server_addr, &addr_len);
        close(sockfd);
        printf("sock recv:%d\n",n);
        if (n > 0) {
            printf("Server replied: %02x,%02x,%02x\n", udp_buf[0], udp_buf[1], udp_buf[2]);
            return 1;
        } else {
            if(type==1)
                printf("meta not response login fail \n");
            else if(type==0)
                printf("meta not response logout fail \n");
            return 0;
        }
        
    }
};

int main(int argc,char* argv[]){
    rclcpp::init(argc,argv);
    auto node =std::make_shared<UdpServerNode>();
    node->init();
    rclcpp::spin(node);
    node->login_meta(0);
    rclcpp::shutdown();
    return 0;
}

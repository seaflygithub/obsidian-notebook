#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/time.h>
#include <linux/spi/spidev.h>
#include <string.h>

#define 	SPI_DEVICE 		"/dev/spidev1.0"
#define 	SPI_MODE 			SPI_MODE_3
#define 	BITS_PER_WORD 	8
#define		READ_LENGTH		0x1000

int gpio_program_b_write(int value)
{
    static const char values_str[] = "01";
    int fd;

    fd = open("/sys/class/gpio/gpio962/value", O_WRONLY);
    if (fd < 0)
    {
        printf("Failed to open gpio value for writing!\n");
        return -1;
    }

    if (write(fd, &values_str[value == 0 ? 0 : 1], 1) < 0)
    {
        printf("Failed to write value!\n");
        close(fd);
        return -1;
    }

    close(fd);
    return 0;
}

int gpio_init_b_read(int value, int timeout)		//ms
{
	int fd;
	int len, loop = 0;
	char buffer[16];

	if( timeout <= 0 )
	{
		timeout = 1;
	}

	for( loop=0; loop<timeout; loop++ )
	{
		fd = open("/sys/class/gpio/gpio961/value", O_RDONLY);
		if (fd < 0)
		{
			printf("Failed to open gpio value for reading!\n");
			return -1;
		}

		if((len=read(fd, buffer, sizeof(buffer))) == -1)
		{
		    perror("read failed!\n");
		    close(fd);
		    return -1;
		}

		buffer[len]=0;
//		printf("value:%d\n", atoi(buffer));
		if( atoi(buffer) == value )
		{
			close(fd);
			return 0;
		}

		close(fd);
		usleep(1000);
	}

	return 1;
}


int gpio_done_read()
{
	int fd;
	int len;
	char buffer[16] = {0};

	fd = open("/sys/class/gpio/gpio960/value", O_RDONLY);
	if (fd < 0)
	{
		printf("Failed to open done gpio value for reading!\n");
		return -1;
	}

	if((len=read(fd, buffer, sizeof(buffer))) == -1)
	{
		perror("read failed!\n");
		close(fd);
		return -1;
	}

	close(fd);

	buffer[len]=0;
//	printf("value:%d\n", atoi(buffer));
	return atoi(buffer);
}

int main(int argc, const char *argv[])
{

	if (argc != 4)
	{
		printf("usage: %s  <spidev>  <Speed_bps> <binfile>\r\n", argv[0]);
		printf("  e.g: %s  /dev/spidev1.0  41666667 /emmc/v13p_0.bin\r\n", argv[0]);
		printf("  e.g: %s  /dev/spidev2.0  41666667 /emmc/v13p_1.bin\r\n", argv[0]);
		return -1;
	}
	const char *spi_device = argv[1];
	unsigned long speed_bps = atoi(argv[2]);
	const char *binfile = argv[3];
	
    int fd, fd_file;
    unsigned char tx[READ_LENGTH] = {0};
    int read_length, is_send_end;
    struct timeval tv1, tv2;
    int cost_ms = 0;
    int file_length, cur_length, print_tag;

	int bits = BITS_PER_WORD;
	int mode = SPI_MODE;


    struct spi_ioc_transfer tr = {
       .tx_buf = (unsigned long)tx,
       .rx_buf = 0,
       .len = sizeof(tx),
	   .speed_hz = speed_bps,
       .delay_usecs = 0,
       .bits_per_word = bits,
    };


	printf("%-16s: %s \r\n",   "spi_device", spi_device);
	printf("%-16s: 0x%x \r\n", "SPI_MODE", mode);
	printf("%-16s: 0x%x \r\n", "BITS_PER_WORD", bits);
	printf("%-16s: %lu \r\n", "speed_bps", speed_bps);
	printf("%-16s: %d \r\n",   "READ_LENGTH", READ_LENGTH);
	printf("%-16s: %s \r\n", "binfile", binfile);




    //open spi device
    fd = open(spi_device, O_RDWR);
    if (fd < 0)
    {
        perror("open spi device failed");
        return -1;
    }

    //set spi mode
    if (ioctl(fd, SPI_IOC_WR_MODE, &mode) < 0)
    {
        perror("set spi mode failed");
        close(fd);
        return -1;
    }

    //set operation bits
    if (ioctl(fd, SPI_IOC_WR_BITS_PER_WORD, &bits) < 0)
    {
        perror("set spi bit per word failed");
        close(fd);
        return -1;
    }

    //set transfer speed
    if (ioctl(fd, SPI_IOC_WR_MAX_SPEED_HZ, &speed_bps) < 0)
    {
        perror("set spi transfer speed failed");
        close(fd);
        return -1;
    }

    fd_file = open(binfile, O_RDONLY);
    if (fd_file < 0)
    {
    	printf("Failed to open bin file for reading!\n");
    	close(fd);
    	return -1;
    }
    file_length = lseek(fd_file, 0, SEEK_END);
    printf("bin file length:%d bytes\n", file_length);
    lseek(fd_file, 0, SEEK_SET);

    gettimeofday(&tv1, NULL);

    cur_length = 0;
    print_tag = 0;
    is_send_end = 0;
    gpio_program_b_write(0);
    if( gpio_init_b_read(0, 10) == 0 )
    {
    	gpio_program_b_write(1);
    	if( gpio_init_b_read(1, 100) == 0 )
    	{
    		while(1)
    		{
    			memset(tx, 0x20, READ_LENGTH);
    			read_length = read(fd_file, tx, READ_LENGTH);
    			if( read_length <= 0 )
    			{
    				printf("bin file transfered end!\n");
    				is_send_end = 1;
    				break;
    			}

    			if (ioctl(fd, SPI_IOC_MESSAGE(1), &tr) < 1)
//    			if( write(fd, tx, READ_LENGTH) != READ_LENGTH )
    			{
    			    perror("SPI transfer failed!\n");
    			    break;
    			}

    			cur_length += read_length;
    			if( cur_length*10/file_length != print_tag )
    			{
    				printf("spi transfer progress:%d\%\n", cur_length*10/file_length*10);
    				print_tag = cur_length*10/file_length;
    			}
    		}
    	}
    	else
    	{
    		printf("The pull-up of the init_b pin cannot be detected.\n");
    	}
    }
    else
    {
    	printf("The pull-down of the init_b pin cannot be detected.\n");
    }

    if( is_send_end == 1 )
    {
    	sleep(1);
    	if( gpio_done_read() == 1 )
    	{
    		printf("vu13p0 bin file has been successfully loaded.\n");
    	}
    }

    gettimeofday(&tv2, NULL);
    cost_ms = (tv2.tv_sec*1000 + tv2.tv_usec/1000) - (tv1.tv_sec*1000 + tv1.tv_usec/1000);
    if( cost_ms <= 0 )
    {
    	cost_ms = 1;
    }
    printf("Send Bin file cost time:%d s\n", cost_ms/1000);

    close(fd);
    close(fd_file);
    return 0;
}    

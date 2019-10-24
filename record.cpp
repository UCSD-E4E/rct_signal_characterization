#include "record.hpp"
#include <uhd.h>
#include <iostream>
#include <thread>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <complex>
#include <fstream>

const size_t SAMPLING_RATE	= 2000000;
const size_t CENTER_FREQ	= 174000000;
const double RF_GAIN		= 20.0;

const size_t RECORD_LEN		= 100 * 1.5 * SAMPLING_RATE;
const size_t RX_BUFFER_LEN	= 2048;

volatile bool run = true;
std::queue<std::complex<short>*> q{};
std::mutex q_m{};
std::condition_variable q_v{};

void displayStatus(int count, int finish){
	double percentComplete = (double)count / finish;
	static const size_t DISPLAY_LEN = 50;
	static const char ZERO_CHAR = ' ';
	static const char COMPLETE_CHAR = '-';
	size_t numChars = DISPLAY_LEN * percentComplete;
	std::cout << '|';
	for(size_t i = 0; i < numChars; i++){
		std::cout << COMPLETE_CHAR;
	}
	for(size_t i = numChars; i < DISPLAY_LEN; i++){
		std::cout << ZERO_CHAR;
	}
	std::cout << "| ";
	std::cout << (int)(percentComplete * 100) << "%, " << count << " of " << finish;
	std::cout << '\r';
	std::cout.flush();

}

std::string uhd_strerror(uhd_error err){
	switch(err){
		case UHD_ERROR_NONE:
			return "None";
		case UHD_ERROR_INVALID_DEVICE:
			return "Invalid device arguments";
		case UHD_ERROR_INDEX:
			return "uhd::index_error";
		case UHD_ERROR_KEY:
			return "uhd::key_error";
		case UHD_ERROR_NOT_IMPLEMENTED:
			return "uhd::not_implemented_error";
		case UHD_ERROR_USB:
			return "uhd::usb_error";
		case UHD_ERROR_IO:
			return "uhd::io_error";
		case UHD_ERROR_OS:
			return "uhd::os_error";
		case UHD_ERROR_ASSERTION:
			return "uhd::assertion_error";
		case UHD_ERROR_LOOKUP:
			return "uhd::lookup_error";
		case UHD_ERROR_TYPE:
			return "uhd::type_error";
		case UHD_ERROR_VALUE:
			return "uhd::value_error";
		case UHD_ERROR_RUNTIME:
			return "uhd::runtime_error";
		case UHD_ERROR_ENVIRONMENT:
			return "uhd::environment_error";
		case UHD_ERROR_SYSTEM:
			return "uhd::system_error";
		case UHD_ERROR_EXCEPT:
			return "uhd::exception";
		case UHD_ERROR_BOOSTEXCEPT:
			return "A boost::exception was thrown";
		case UHD_ERROR_STDEXCEPT:
			return "A std::exception was thrown.";
		case UHD_ERROR_UNKNOWN:
		default:
			return "An unknown error was thrown.";
	}
}

void writer();

int main(int argc, char const *argv[])
{
	/* code */

	std::string cpu_format("sc16");
	std::string wire_format("sc16");

	uhd_usrp_handle usrp;
	uhd_rx_streamer_handle rx_streamer;
	uhd_error error = uhd_usrp_make(&usrp, "");
	if(error != UHD_ERROR_NONE){
		std::cerr << "UHD Error creating USRP: " << uhd_strerror(error) << std::endl;
		return -1;
	}
	uhd_rx_streamer_make(&rx_streamer);
	// Set sampling rate on CH0 to 2 MSPS
	uhd_usrp_set_rx_rate(usrp, SAMPLING_RATE, 0);

	// Get sampling rate and confirm
	double value{0};
	uhd_usrp_get_rx_rate(usrp, 0, &value);
	if((value / SAMPLING_RATE) - 1.0 > 1e-2){
		std::cerr << "Sampling rate not correctly set! Rate is " << value << std::endl;
		return -1;
	}

	// set RF gain
	uhd_usrp_set_rx_gain(usrp, RF_GAIN, 0, "");

	// get rf gain and confirm
	uhd_usrp_get_rx_gain(usrp, 0, "", &value);
	if((value / RF_GAIN) - 1.0 > 1e-2){
		std::cerr << "Receive gain not correctly set!  Gain is " << value << std::endl;
		return -1;
	}

	// set center frequency
	uhd_tune_request_t tune_request{};
	tune_request.target_freq = CENTER_FREQ;
	tune_request.rf_freq_policy = UHD_TUNE_REQUEST_POLICY_AUTO;
	tune_request.dsp_freq_policy = UHD_TUNE_REQUEST_POLICY_AUTO;
	
	uhd_tune_result_t tune_result{};

	uhd_usrp_set_rx_freq(usrp, &tune_request, 0, &tune_result);

	if((tune_result.actual_rf_freq / CENTER_FREQ) - 1.0 > 1e-2){
		std::cerr << "Center frequency not correctly set!  Frequency is " << tune_result.actual_rf_freq << std::endl;
		return -1;
	}

	// configure stream
	uhd_stream_args_t stream_args{};
	stream_args.cpu_format = new char[1024];
	std::strcpy(stream_args.cpu_format, cpu_format.c_str());
	stream_args.otw_format = new char[1024];
	std::strcpy(stream_args.otw_format, wire_format.c_str());
	stream_args.args = new char[1024];
	std::strcpy(stream_args.args, "num_recv_frames=512");

	size_t* channel_nums = new size_t[1];
	channel_nums[0] = 0;
	stream_args.channel_list = channel_nums;
	stream_args.n_channels = 1;

	error = uhd_usrp_get_rx_stream(usrp, &stream_args, rx_streamer);
	if(error != UHD_ERROR_NONE){
		std::cerr << "UHD Error configuring stream: " << uhd_strerror(error) << std::endl;
		return -1;
	}

	// start stream
	uhd_stream_cmd_t stream_cmd{};
	stream_cmd.stream_mode = UHD_STREAM_MODE_START_CONTINUOUS;
	stream_cmd.stream_now = true;

	uhd_rx_metadata_handle md{};
	uhd_rx_metadata_make(&md);
	size_t total_samples = 0;
	size_t num_samps = 0;

	std::thread t{writer};

	uhd_rx_streamer_issue_stream_cmd(rx_streamer, &stream_cmd);
	while(total_samples < RECORD_LEN){
		std::complex<int16_t>* raw_buffer = new std::complex<int16_t>[RX_BUFFER_LEN];
		uhd_rx_streamer_recv(rx_streamer, (void**) &raw_buffer, RX_BUFFER_LEN, &md, 1.0, false, &num_samps);
		total_samples += num_samps;
		std::unique_lock<std::mutex> lock{q_m};
		q.push(raw_buffer);
		lock.unlock();
		q_v.notify_all();
		displayStatus(total_samples, RECORD_LEN);
	}
	std::cout << std::endl << "Received " << total_samples << " samples" << std::endl;


	t.join();

	stream_cmd.stream_mode =  UHD_STREAM_MODE_STOP_CONTINUOUS;
	uhd_rx_streamer_issue_stream_cmd(rx_streamer, &stream_cmd);
	uhd_rx_metadata_free(&md);
	return 0;
}

void writer(){
	size_t written_samples = 0;
	std::ofstream ostr{"output", std::ios::binary | std::ios::out};
	uint16_t maxI = 0;
	uint16_t maxQ = 0;
	while(written_samples < RECORD_LEN){
		std::unique_lock<std::mutex> lock{q_m};
		if(q.empty()){
			q_v.wait(lock);
		}
		if(!q.empty()){
			std::complex<int16_t>* buffer = q.front();
			q.pop();
			lock.unlock();
			ostr.write((char*) buffer, RX_BUFFER_LEN * 2 * sizeof(int16_t));
			written_samples += RX_BUFFER_LEN;
			for(size_t i = 0; i < RX_BUFFER_LEN; i++){
				if(buffer[i].real() > maxI){
					maxI = buffer[i].real();
				}
				if(buffer[i].imag() > maxQ){
					maxQ = buffer[i].imag();
				}
			}
			delete[] buffer;
		}
	}
	std::cout << "Recorded " << written_samples << " samples" << std::endl;
	std::cout << "Maximum in-phase recorded: " << maxI << " of " << INT16_MAX << std::endl;
	std::cout << "Maximum quadrature recorded: " << maxQ << " of " << INT16_MAX << std::endl;
	ostr.close();
}
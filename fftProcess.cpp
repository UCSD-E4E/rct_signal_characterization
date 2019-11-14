#include <iostream>
#include <fstream>
#include <fftw3.h>
#include <complex>
#include <sys/stat.h>

const size_t FFT_LEN	=	2048;
const size_t FFT_STRIDE	=	2048;

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

int main(int argc, char const *argv[]){
	const int NUM_FFT = 2;
	// if(!fftw_init_threads()){
	// 	std::cerr << "Failed to initialize FFTW threads!" << std::endl;
	// }
	fftw_complex* fft_in = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * FFT_LEN * NUM_FFT);
	if(fft_in == nullptr){
		std::cerr << "Failed to allocate fft_in!" << std::endl;
		return -1;
	}
	fftw_complex* fft_out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * FFT_LEN * NUM_FFT);
	if(fft_out == nullptr){
		std::cerr << "Failed to allocate fft_out!" << std::endl;
		return -1;
	}


	// fftw_plan_with_nthreads(1);

	int fft_size[] = {FFT_LEN};
	const int FFT_DIST = 1;

	fftw_plan fft_plan = fftw_plan_many_dft(1, fft_size, NUM_FFT, fft_in, NULL, NUM_FFT, FFT_DIST, fft_out, NULL, NUM_FFT, FFT_DIST, FFTW_FORWARD, FFTW_MEASURE);

	std::ifstream inFile{"output", std::ios::binary | std::ios::in};
	std::ofstream outFile{"processedOutput", std::ios::binary | std::ios::out};
	struct stat st;
	if(stat("output", &st) != 0){
		return -1;
	}
	size_t inputSize = st.st_size / 2 / sizeof(int16_t);

	int16_t* unpack = new int16_t[FFT_LEN * 2];
	int16_t* repack = new int16_t[2 * FFT_LEN];
	size_t numSamples = 0;
	bool run = true;
	double maxI = 0;
	double maxQ = 0;
	while(run){
		inFile.read((char*) unpack, FFT_LEN * 2 * sizeof(int16_t));
		size_t read = inFile.gcount();
		numSamples += read / 2 / sizeof(int16_t);
		if(read < FFT_LEN * 2 * sizeof(int16_t)){
			run = false;
		}
		for(size_t i = 0; i < FFT_LEN; i++){
			fft_in[i][0] = double(unpack[2 * i]);
			fft_in[i][1] = double(unpack[2 * i + 1]);
		}
		fftw_execute(fft_plan);
		for(size_t i = 0; i < FFT_LEN; i++){
			repack[2 * i] = fft_out[i][0] / FFT_LEN;
			repack[2 * i + 1] = fft_out[i][1] / FFT_LEN;
			if(repack[2 * i + 0] > maxI){
				maxI = repack[2 * i + 0];
			}
			if(repack[2 * i + 1] > maxQ){
				maxQ = repack[2 * i + 1];
			}
		}
		outFile.write((char*)repack, FFT_LEN * 2 * sizeof(int16_t));
		displayStatus(numSamples, inputSize);
	}
	std::cout << std::endl;
	std::cout << "Max in-phase: " << maxI << std::endl;
	std::cout << "Max quadrature: " << maxQ << std::endl;

	delete[] unpack;
	outFile.close();
	inFile.close();
	fftw_destroy_plan(fft_plan);
	fftw_cleanup();
	fftw_free(fft_out);
	fftw_free(fft_in);
	// fftw_cleanup_threads();
	return 0;
}
// main.cpp : Defines the entry point for the application.
//
#include <algorithm>
#include <iostream>
#include <vector>
#include <string>
#include <stdexcept>
#include <string_view>
#include <utils/string_utils.h>

using namespace std;

int main(int argc, char* argv[])
{
	cout << "=== numbers_transofm ===" << endl;
	
	std::string s = "0.8/11/2.8/3/2	115";
	auto nums_s = utils::split_of(s, " \t/");
	std::vector<float> nums;
	std::transform(nums_s.begin(), nums_s.end(), std::back_inserter(nums), [](auto&& sv) {
		return std::stof(std::string(sv));
	});
	return 0;
}

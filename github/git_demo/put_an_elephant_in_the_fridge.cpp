#include<iostream>
using namespace std;

void open_the_fridge() {
    // add code here
   cout << "The fridge is now open." << endl;
}
void put_the_elephant_in() {
    // add code here
    // user B
    cout << "The elephant is now in the fridge, with some bananas." << endl;
}
void close_the_fridge() {
    // add code here
    // user B
    cout << "The fridge is now closed." << endl;
}

void warning() {
    cout << "this function is not implemented yet!" << endl;
}

void put_the_elephant_in_the_fridge() {
    // warning();
    open_the_fridge();
    put_the_elephant_in();
    close_the_fridge();
}

int main() {
    put_the_elephant_in_the_fridge();
    return 0;
}

#include <chrono>
#include <stdexcept>
#include <thread>

extern "C" int slow_function() {
  std::this_thread::sleep_for(std::chrono::milliseconds(500));
  return 42;
}

void background_exception_thrower() {
  while (true) {
    try {
      throw std::runtime_error("background exception");
    } catch (...) {
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
  }
}

int main() {
  std::thread thrower(background_exception_thrower);
  thrower.detach();

  // Break here and run `expr slow_function()` to reproduce
  int dummy = 0;

  return dummy;
}

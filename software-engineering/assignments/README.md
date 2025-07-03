# 软件工程 习题

## 1 避免嵌套

重构下面代码，使其嵌套不超过两层：
```cpp
bool CoffeeMaker::makeCoffee(CoffeeType type, int coffee_number) {
    for (int i = 0; i < coffee_number; ++i) {
        if (this->water > 0) {
            if (this->cup > 0) {
                if (this->coffee_beans > 0) {
                    if (this->supportCoffeeType(type)) {
                        if (this->hasElectricity()) {
                            // Finally, we are making coffee...
                        } else {
                            throw CoffeeMakerNoPowerException();
                        }
                    } else {
                        throw CoffeeTypeNotSupportedException();
                    }
                } else {
                    throw RunOutOfCoffeeBeansException();
                }
            } else {
                throw RunOutOfCupException();
            }
        } else {
            throw RunOutOfWaterException();
        }
    }
    return true;
}
```

## 2 测试先行

利用测试先行方法完成 `src/geometry.py` 中的两个函数。具体的过程大致为——为两个函数设计测例，放入 `test/test_geometry.py` 中，之后编写函数的目标变为通过所有测例。

编写完成之后如果发现 bug，则将会产生 bug 的输入作为测例，并 assert 代码产生正确输出；改掉 bug 的目标便是令此测例通过。

## 3 编写测试

为 `src/priority_queue.py` 编写测例，放在 `test/test_priority_queue.py` 中。`src/priority.py` 的实现并不一定正确，请尝试通过编写测例的方式找到其中的 bug。

## 4 实践其他代码风格

好的代码风格不止 Reading 中提到的几条，实际上还包括：
- 避免魔鬼数字(Avoid Magic Number)：对于程序中出现的常量，不要以字面值的形式直接使用，而是将其定义成常量
- 不要使用全局变量。
- 一个函数不能太长，一行也不能过长。
- 不要单独处理特例；如果你的算法是正确的，那么它对于退化输入也应该是正确的。

请重构 `cpp/bad_style.cpp`，规范其代码风格。


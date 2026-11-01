<?php

use App\Calculator;
use PHPUnit\Framework\TestCase;

class CalculatorTest extends TestCase
{
    public function testAdd()
    {
        $c = new Calculator();
        $this->assertEquals(5, $c->add(2, 3));
    }

    public function testSubtract()
    {
        $c = new Calculator();
        $this->assertEquals(-1, $c->subtract(2, 3));
    }

    public function testDivide()
    {
        $c = new Calculator();
        $this->assertEquals(2.5, $c->divide(5, 2));
    }

    public function testDivideByZero()
    {
        $this->expectException(InvalidArgumentException::class);
        $c = new Calculator();
        $c->divide(1, 0);
    }
}
